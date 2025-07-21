
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="لوحة التداول الذكي", layout="wide")

st.title("📈 لوحة تحكم التداول الذكي")
st.markdown("مبنية على تحليلات صور القاما وذكاء اصطناعي تنبؤي.")

# تحميل الملف
@st.cache_data
def load_data():
    return pd.read_csv("executed_trades.csv")

df = load_data()

# تنسيق الوقت
df['entry_time'] = pd.to_datetime(df['entry_time'])

# احتساب النتائج
df['pnl_value'] = df['exit_price'] - df['entry_price']
df['profitable'] = df['pnl_value'].apply(lambda x: 1 if x > 0 else 0)
df['pnl_cumsum'] = df['pnl_value'].cumsum()

# التصفية الجانبية
st.sidebar.header("🎛️ التصفية")

symbols = df['symbol'].unique().tolist()
entry_types = df['entry_type'].unique().tolist()

selected_symbols = st.sidebar.multiselect("رموز:", symbols, default=symbols)
selected_types = st.sidebar.multiselect("نوع الصفقة:", entry_types, default=entry_types)

min_date = df['entry_time'].min().date()
max_date = df['entry_time'].max().date()
selected_dates = st.sidebar.date_input("نطاق التاريخ:", [min_date, max_date])

only_winners = st.sidebar.checkbox("✅ عرض الصفقات الرابحة فقط")
only_rejected = st.sidebar.checkbox("❌ عرض المرفوضة من النموذج")

# تطبيق الفلاتر
filtered_df = df[
    df['symbol'].isin(selected_symbols) &
    df['entry_type'].isin(selected_types) &
    (df['entry_time'].dt.date >= selected_dates[0]) &
    (df['entry_time'].dt.date <= selected_dates[1])
]

if only_winners:
    filtered_df = filtered_df[filtered_df['profitable'] == 1]

if only_rejected:
    filtered_df = filtered_df[filtered_df['model_decision'] == 0]

# عرض الإحصائيات
col1, col2, col3, col4 = st.columns(4)
col1.metric("إجمالي الصفقات", len(filtered_df))
col2.metric("نسبة النجاح", f"{filtered_df['profitable'].mean()*100:.2f}%")
col3.metric("إجمالي الربح", f"{filtered_df['pnl_value'].sum():.2f}")
col4.metric("متوسط الثقة", f"{filtered_df['confidence_score'].mean():.1f}")

st.divider()

# جدول الصفقات
st.subheader("📋 الصفقات")
st.dataframe(filtered_df.sort_values('entry_time', ascending=False), use_container_width=True)

# رسم الربح التراكمي
fig1 = px.line(filtered_df, x='entry_time', y='pnl_cumsum', title='📈 الأداء التراكمي', markers=True)
st.plotly_chart(fig1, use_container_width=True)

# توزيع حسب النوع
col5, col6 = st.columns(2)
with col5:
    fig2 = px.histogram(filtered_df, x='entry_type', color='profitable', barmode='group', title='🔁 نوع الصفقة')
    st.plotly_chart(fig2, use_container_width=True)

with col6:
    fig3 = px.histogram(filtered_df, x='symbol', color='profitable', barmode='group', title='📊 حسب الرمز')
    st.plotly_chart(fig3, use_container_width=True)
