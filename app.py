import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 파일 설정
TRADE_FILE = 'investments.csv'
COST_FILE = 'fixed_costs.csv'

# 데이터 로드 함수
def load_data(file, columns):
    if os.path.exists(file):
        try:
            return pd.read_csv(file)
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# 데이터 저장 함수
def save_data(df, file):
    df.to_csv(file, index=False, encoding='utf-8-sig')

st.set_page_config(layout="wide", page_title="Stock Journal Pro")
st.title("📈 주식 매매 관리 (수정/삭제 기능 추가)")

# --- 사이드바: 고정비 관리 ---
st.sidebar.header("💰 고정비(리딩비) 관리")
costs = load_data(COST_FILE, ['날짜', '금액', '항목'])

with st.sidebar.expander("비용 추가"):
    with st.form("cost_form", clear_on_submit=True):
        c_date = st.date_input("발생일", datetime.now())
        c_amt = st.number_input("금액 (마이너스 입력)", value=-100000)
        c_memo = st.text_input("항목명", "월 리딩비")
        if st.form_submit_button("추가"):
            new_c = pd.DataFrame([{'날짜': c_date, '금액': c_amt, '항목': c_memo}])
            costs = pd.concat([costs, new_c], ignore_index=True)
            save_data(costs, COST_FILE)
            st.rerun()

if not costs.empty:
    st.sidebar.markdown("---")
    st.sidebar.subheader("고정비 내역 관리")
    # 고정비 삭제 기능
    edited_costs = st.sidebar.data_editor(costs, num_rows="dynamic", key="cost_editor")
    if st.sidebar.button("고정비 변경사항 저장"):
        save_data(edited_costs, COST_FILE)
        st.rerun()

# --- 메인: 입력 섹션 ---
trades = load_data(TRADE_FILE, ['종목명','매수날짜','매수량','매수단가','매도날짜','매도량','매도단가'])

with st.expander("➕ 새 매매 기록 추가", expanded=False):
    with st.form("trade_form", clear_on_submit=True):
        name = st.text_input("종목명")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**[매수]**")
            b_date = st.date_input("매수일", datetime.now())
            b_qty = st.number_input("매수량", min_value=0)
            b_prc = st.number_input("매수단가", min_value=0)
        with col2:
            st.markdown("**[매도]**")
            s_date = st.date_input("매도일", datetime.now())
            s_qty = st.number_input("매도량", min_value=0)
            s_prc = st.number_input("매도단가", min_value=0)
        
        if st.form_submit_button("기록 저장"):
            new_t = pd.DataFrame([{
                '종목명': name, '매수날짜': b_date, '매수량': b_qty, '매수단가': b_prc,
                '매도날짜': s_date, '매도량': s_qty, '매도단가': s_prc
            }])
            trades = pd.concat([trades, new_t], ignore_index=True)
            save_data(trades, TRADE_FILE)
            st.rerun()

# --- 데이터 수정 및 삭제 (관리자 모드) ---
with st.expander("🛠️ 데이터 수정 및 삭제 (여기서 직접 수정 가능)"):
    st.info("표 안의 내용을 클릭해서 수정하거나, 왼쪽 체크박스를 선택 후 [Delete] 키로 삭제할 수 있습니다.")
    edited_trades = st.data_editor(trades, num_rows="dynamic", key="trade_editor")
    if st.button("매매 내역 변경사항 최종 저장"):
        save_data(edited_trades, TRADE_FILE)
        st.success("데이터가 업데이트되었습니다!")
        st.rerun()

# --- 데이터 표시 (이미지 디자인 구현) ---
st.subheader("📋 투자 내역 현황 (Dashboard)")

if not trades.empty:
    html_code = """
    <style>
        .stock-table { width: 100%; border-collapse: collapse; text-align: center; }
        .stock-table th, .stock-table td { border: 1px solid #ddd; padding: 10px; }
        .stock-table th { background-color: #f2f2f2; font-weight: bold; }
        .buy-row { background-color: #ffffff; }
        .sell-row { background-color: #f9f9f9; }
    </style>
    <table class="stock-table">
        <tr>
            <th>종목명</th><th>구분</th><th>날짜</th><th>수량</th><th>단가</th><th>총금액</th><th>수익금액</th><th>수익률</th>
        </tr>
    """
    
    for _, row in trades.iterrows():
        # 데이터가 비어있을 경우 에러 방지
        try:
            b_total = float(row['매수량']) * float(row['매수단가'])
            s_total = float(row['매도량']) * float(row['매도단가'])
            profit = s_total - b_total
            rate = (profit / b_total * 100) if b_total > 0 else 0
            
            p_color = "red" if profit > 0 else ("blue" if profit < 0 else "black")
            
            html_code += f"""
            <tr class="buy-row">
                <td rowspan="2"><b>{row['종목명']}</b></td>
                <td>매수</td><td>{row['매수날짜']}</td><td>{row['매수량']:,}</td><td>{row['매수단가']:,}</td><td>{b_total:,.0f}</td>
                <td rowspan="2" style="color:{p_color}; font-weight:bold;">{profit:,.0f}</td>
                <td rowspan="2" style="color:{p_color}; font-weight:bold;">{rate:.1f}%</td>
            </tr>
            <tr class="sell-row">
                <td>매도</td><td>{row['매도날짜']}</td><td>{row['매도량']:,}</td><td>{row['매도단가']:,}</td><td>{s_total:,.0f}</td>
            </tr>
            """
        except:
            continue
            
    html_code += "</table>"
    st.markdown(html_code, unsafe_allow_html=True)

# --- 하단 정산 ---
st.divider()
total_trade = 0
if not trades.empty:
    try:
        total_trade = (trades['매도량'].astype(float)*trades['매도단가'].astype(float)).sum() - \
                      (trades['매수량'].astype(float)*trades['매수단가'].astype(float)).sum()
    except: pass

total_cost = costs['금액'].sum() if not costs.empty else 0
net_profit = total_trade + total_cost

c1, c2, c3 = st.columns(3)
c1.metric("매매 총수익", f"{total_trade:,.0f}원")
c2.metric("고정비 합계", f"{total_cost:,.0f}원", delta_color="inverse")
c3.metric("최종 순수익", f"{net_profit:,.0f}원")
