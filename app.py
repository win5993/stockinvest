import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 파일 설정 및 데이터 로드
TRADE_FILE = 'investments.csv'
COST_FILE = 'fixed_costs.csv'

def load_data(file, columns):
    if os.path.exists(file):
        try: return pd.read_csv(file)
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False, encoding='utf-8-sig')

# 앱 설정
st.set_page_config(layout="wide", page_title="주식 투자 일지")
st.title("📊 주식 매매 관리 시스템")

# --- 2. 사이드바: 고정비(리딩비) 관리 ---
st.sidebar.header("💰 고정비 관리")
costs = load_data(COST_FILE, ['날짜', '금액', '항목'])

with st.sidebar.expander("비용 입력", expanded=False):
    with st.form("cost_form", clear_on_submit=True):
        c_date = st.date_input("날짜", datetime.now())
        c_amt = st.number_input("금액 (마이너스)", value=-100000)
        c_memo = st.text_input("항목명", "월 리딩비")
        if st.form_submit_button("저장"):
            costs = pd.concat([costs, pd.DataFrame([{'날짜': c_date, '금액': c_amt, '항목': c_memo}])], ignore_index=True)
            save_data(costs, COST_FILE)
            st.rerun()

if not costs.empty:
    st.sidebar.write("---")
    st.sidebar.subheader("고정비 내역")
    edited_costs = st.sidebar.data_editor(costs, num_rows="dynamic", key="ce")
    if st.sidebar.button("비용 수정사항 저장"):
        save_data(edited_costs, COST_FILE)
        st.rerun()

# --- 3. 메인: 매매 기록 입력 ---
trades = load_data(TRADE_FILE, ['종목명','매수날짜','매수량','매수단가','매도날짜','매도량','매도단가'])

with st.expander("➕ 새 매매 기록 추가", expanded=False):
    with st.form("trade_form", clear_on_submit=True):
        name = st.text_input("종목명")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**[매수 기록]**")
            b_date = st.date_input("매수일", datetime.now(), key="b1")
            b_qty = st.number_input("매수량", min_value=0, key="b2")
            b_prc = st.number_input("매수단가", min_value=0, key="b3")
        with col2:
            st.markdown("**[매도 기록]**")
            s_date = st.date_input("매도일", datetime.now(), key="s1")
            s_qty = st.number_input("매도량", min_value=0, key="s2")
            s_prc = st.number_input("매도단가", min_value=0, key="s3")
        if st.form_submit_button("매매 내역 저장"):
            new_t = pd.DataFrame([{'종목명': name, '매수날짜': b_date, '매수량': b_qty, '매수단가': b_prc, '매도날짜': s_date, '매도량': s_qty, '매도단가': s_prc}])
            trades = pd.concat([trades, new_t], ignore_index=True)
            save_data(trades, TRADE_FILE)
            st.rerun()

# --- 4. 데이터 수정 및 삭제 ---
with st.expander("🛠️ 데이터 수정/삭제 (여기서 지우거나 수정 가능)"):
    edited_trades = st.data_editor(trades, num_rows="dynamic", key="te")
    if st.button("매매 내역 변경사항 저장"):
        save_data(edited_trades, TRADE_FILE)
        st.success("저장되었습니다!")
        st.rerun()

# --- 5. 투자 현황판 (디자인 재현 및 HTML 오류 수정) ---
st.subheader("📋 투자 현황판")

if not trades.empty:
    # 스타일 및 표 생성 시작
    html_code = """
    <div style="overflow-x:auto;">
    <table style="width:100%; border-collapse:collapse; text-align:center; border:1px solid #444; font-family:sans-serif;">
        <thead style="background-color:#f8f9fa;">
            <tr>
                <th style="border:1px solid #444; padding:10px;">종목명</th>
                <th style="border:1px solid #444; padding:10px;">매수날짜</th>
                <th style="border:1px solid #444; padding:10px;">매수량</th>
                <th style="border:1px solid #444; padding:10px;">매수단가</th>
                <th style="border:1px solid #444; padding:10px;">총매수금액</th>
                <th style="border:1px solid #444; padding:10px;">수익금액</th>
                <th style="border:1px solid #444; padding:10px;">수익률</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for _, row in trades.iterrows():
        try:
            b_qty = float(row['매수량'])
            b_prc = float(row['매수단가'])
            s_qty = float(row['매도량'])
            s_prc = float(row['매도단가'])
            
            b_total = b_qty * b_prc
            s_total = s_qty * s_prc
            profit = s_total - b_total
            rate = (profit / b_total * 100) if b_total > 0 else 0
            
            p_color = "red" if profit > 0 else ("blue" if profit < 0 else "black")
            
            # 3단 구조 레이아웃 (이미지 image_5db524.png 참조)
            html_code += f"""
            <tr>
                <td rowspan="3" style="border:1px solid #444; font-weight:bold;">{row['종목명']}</td>
                <td style="border:1px solid #444;">{row['매수날짜']}</td>
                <td style="border:1px solid #444;">{b_qty:,.0f}</td>
                <td style="border:1px solid #444;">{b_prc:,.0f}</td>
                <td style="border:1px solid #444;">{b_total:,.0f}</td>
                <td rowspan="3" style="border:1px solid #444; color:{p_color}; font-weight:bold;">{profit:,.0f}</td>
                <td rowspan="3" style="border:1px solid #444; color:{p_color}; font-weight:bold;">{rate:.1f}%</td>
            </tr>
            <tr style="background-color:#fafafa;">
                <td style="border:1px solid #444; font-size:0.9em; font-weight:bold;">매도날짜</td>
                <td style="border:1px solid #444; font-size:0.9em; font-weight:bold;">매도량</td>
                <td style="border:1px solid #444; font-size:0.9em; font-weight:bold;">매도단가</td>
                <td style="border:1px solid #444; font-size:0.9em; font-weight:bold;">총매도금액</td>
            </tr>
            <tr>
                <td style="border:1px solid #444;">{row['매도날짜']}</td>
                <td style="border:1px solid #444;">{s_qty:,.0f}</td>
                <td style="border:1px solid #444;">{s_prc:,.0f}</td>
                <td style="border:1px solid #444;">{s_total:,.0f}</td>
            </tr>
            """
        except: continue
            
    html_code += "</tbody></table></div>"
    
    # HTML 렌더링 (가장 중요한 부분)
    st.markdown(html_code, unsafe_allow_html=True)

# --- 6. 하단 총 정산 ---
total_trade = 0
if not trades.empty:
    try:
        total_trade = (trades['매도량'].astype(float)*trades['매도단가'].astype(float)).sum() - \
                      (trades['매수량'].astype(float)*trades['매수단가'].astype(float)).sum()
    except: pass

total_cost = costs['금액'].sum() if not costs.empty else 0
net_profit = total_trade + total_cost

st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("매매 총수익", f"{total_trade:,.0f}원")
c2.metric("고정비 합계", f"{total_cost:,.0f}원", delta_color="inverse")
c3.metric("최종 순수익", f"{net_profit:,.0f}원")
