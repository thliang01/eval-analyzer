import json
import io
from typing import List, Dict, Tuple

import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
from pathlib import PurePosixPath

st.set_page_config(page_title="Twinkle Eval Analyzer", page_icon=":star2:", layout="wide")

st.title("✨ Twinkle Eval Analyzer (.json / .jsonl)")

# ----------------- Helpers -----------------

def _decode_bytes_to_text(b: bytes) -> str:
    for enc in ("utf-8", "utf-16", "utf-16le", "utf-16be", "big5", "cp950"):
        try:
            return b.decode(enc)
        except Exception:
            continue
    return b.decode("utf-8", errors="ignore")

def read_twinkle_doc(file) -> Dict:
    raw = file.read()
    if isinstance(raw, bytes):
        text = _decode_bytes_to_text(raw)
    else:
        text = raw
    text = text.strip()
    try:
        obj = json.loads(text)
    except Exception:
        for line in text.splitlines():
            line = line.strip().rstrip(",")
            if not line:
                continue
            try:
                obj = json.loads(line)
                break
            except Exception:
                continue
    if not isinstance(obj, dict):
        raise ValueError("檔案不是有效的 Twinkle Eval JSON 物件。")
    if "timestamp" not in obj or "config" not in obj or "dataset_results" not in obj:
        raise ValueError("缺少必要欄位")
    return obj

def extract_records(doc: Dict) -> Tuple[pd.DataFrame, Dict[str, float]]:
    model = doc.get("config", {}).get("model", {}).get("name", "<unknown>")
    timestamp = doc.get("timestamp", "<no-ts>")
    source_label = f"{model} @ {timestamp}"
    rows = []
    avg_map = {}
    for ds_path, ds_payload in doc.get("dataset_results", {}).items():
        ds_name = ds_path.split("datasets/")[-1].strip("/") if ds_path.startswith("datasets/") else ds_path
        avg_meta = ds_payload.get("average_accuracy") if isinstance(ds_payload, dict) else None
        results = ds_payload.get("results", []) if isinstance(ds_payload, dict) else []
        for item in results:
            if not isinstance(item, dict):
                continue
            file_path = item.get("file")
            acc_mean = item.get("accuracy_mean")
            if file_path is None or acc_mean is None:
                continue
            fname = PurePosixPath(file_path).name
            category = fname.rsplit(".", 1)[0]
            rows.append({
                "dataset": ds_name,
                "category": category,
                "file": fname,
                "accuracy_mean": float(acc_mean),
                "source_label": source_label
            })
        if avg_meta is None and results:
            vals = [float(it.get("accuracy_mean", np.nan)) for it in results if "accuracy_mean" in it]
            if vals:
                avg_meta = float(np.mean(vals))
        if avg_meta is not None:
            avg_map[ds_name] = avg_meta
    return pd.DataFrame(rows), avg_map

def load_all(files) -> Tuple[pd.DataFrame, Dict[str, Dict[str, float]]]:
    frames = []
    meta = {}
    for f in files or []:
        try:
            doc = read_twinkle_doc(f)
        except Exception as e:
            st.error(f"❌ 無法讀取 {getattr(f, 'name', '檔案')}：{e}")
            continue
        df, avg_map = extract_records(doc)
        if not df.empty:
            frames.append(df)
            src = df["source_label"].iloc[0]
            meta[src] = avg_map
    if not frames:
        return pd.DataFrame(columns=["dataset", "category", "file", "accuracy_mean", "source_label"]), {}
    return pd.concat(frames, ignore_index=True), meta

# ----------------- Sidebar -----------------

with st.sidebar:
    files = st.file_uploader("選擇 Twinkle Eval 檔案", type=["json", "jsonl"], accept_multiple_files=True)
    df_all, meta_all = load_all(files)
    normalize_0_100 = st.checkbox("以 0–100 顯示", value=False)
    page_size = st.selectbox("每張圖顯示幾個類別", [10, 20, 30, 50, 100], index=1)
    sort_mode = st.selectbox("排序方式", ["依整體平均由高到低", "依整體平均由低到高", "依字母排序"])

if df_all.empty:
    st.info("請上傳 Twinkle Eval 檔案")
    st.stop()

all_datasets = sorted(df_all["dataset"].unique().tolist())
selected_dataset = st.selectbox("選擇資料集", options=all_datasets)
work = df_all[df_all["dataset"] == selected_dataset].copy()
metric_plot = "accuracy_mean" + (" (x100)" if normalize_0_100 else "")
work[metric_plot] = work["accuracy_mean"] * (100.0 if normalize_0_100 else 1.0)

order_df = work.groupby("category")[metric_plot].mean().reset_index()
if sort_mode == "依整體平均由高到低":
    order_df = order_df.sort_values(metric_plot, ascending=False)
elif sort_mode == "依整體平均由低到高":
    order_df = order_df.sort_values(metric_plot, ascending=True)
else:
    order_df = order_df.sort_values("category", ascending=True)

cat_order = order_df["category"].tolist()
work["category"] = pd.Categorical(work["category"], categories=cat_order, ordered=True)

n = len(cat_order)
pages = int(np.ceil(n / page_size))

for p in range(pages):
    start, end = p * page_size, min((p + 1) * page_size, n)
    subset_cats = cat_order[start:end]
    sub = work[work["category"].isin(subset_cats)]
    st.subheader(f"📊 {selected_dataset}｜類別 {start+1}-{end} / {n}")
    base = alt.Chart(sub).encode(
        x=alt.X("category:N", sort=subset_cats),
        y=alt.Y(f"{metric_plot}:Q"),
        color=alt.Color("source_label:N"),
        tooltip=["source_label", "file", alt.Tooltip(metric_plot, format=".3f")]
    )
    bars = base.mark_bar().encode(xOffset="source_label")
    st.altair_chart(bars.properties(height=420), use_container_width=True)
    pivot = sub.pivot_table(index="category", columns="source_label", values=metric_plot)
    st.dataframe(pivot, use_container_width=True)
    st.download_button(
        label=f"下載此頁 CSV ({start+1}-{end})",
        data=pivot.reset_index().to_csv(index=False).encode("utf-8"),
        file_name=f"twinkle_{selected_dataset}_{start+1}_{end}.csv",
        mime="text/csv"
    )
