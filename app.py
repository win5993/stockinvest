import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 파일 설정
TRADE_FILE = 'investments.csv'
COST_FILE = 'fixed_costs.csv'

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

# 앱 설정
st.set_page_config(layout="wide", page_title="Stock Journal")
st.title("📊 프리미엄 투자 관리 대시보드")

# --- 사이드바: 월간 고정비(리딩비) 관리 ---
st.sidebar.header("💰 고정비 관리 (리딩비 등)")
with st.sidebar.form("cost_form", clear_on_submit=True):
    cost_date = st.date_input("비용 발생일", datetime.now())
    cost_amount = st.number_input("금액 (마이너스로 입력)", value=-100000, step=10000)
    cost_memo = st.text_input("항목 (예: 1월 리딩비)")
    if st.form_submit_button("비용 기록"):
        costs = load_data(COST_FILE, ['날짜', '금액', '항목'])
        new_cost = pd.DataFrame([{'날짜': cost_date, '금액': cost_amount, '항목': cost_memo}])
        pd.concat([costs, new_cost]).to_csv(COST_FILE, index=False, encoding='utf-8-sig')
        st.success("고정비가 반영되었습니다.")

# --- 메인: 종목 매매 기록 입력 ---
st.header("📝 종목 매매 기록")
with st.expander("새로운 매매 기록 추가", expanded=True):
    with st.form("trade_form", clear_on_submit=True):
        stock_name = st.text_input("종목명")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("매수 정보")
            b_date = st.date_input("매수 날짜", datetime.now())
            b_qty = st.number_input("매수량", min_value=1, step=1)
            b_price = st.number_input("매수 단가", min_value=0, step=100)
            
        with col2:
            st.subheader("매도 정보")
            s_date = st.date_input("매도 날짜", datetime.now())
            s_qty = st.number_input("매도량", min_value=1, step=1)
            s_price = st.number_input("매도 단가", min_value=0, step=100)
            
        if st.form_submit_button("매매 내역 저장"):
            trades = load_data(TRADE_FILE, ['종목명', '매수날짜', '매수량', '매수단가', '매도날짜', '매도량', '매도단가'])
            new_trade = pd.DataFrame([{
                '종목명': stock_name, '매수날짜': b_date, '매수량': b_qty, '매수단가': b_price,
                '매도날짜': s_date, '매도량': s_qty, '매도단가': s_price
            }])
            pd.concat([trades, new_trade]).to_csv(TRADE_FILE, index=False, encoding='utf-8-sig')
            st.rerun()

# --- 데이터 표시 (이미지 레이아웃 구현) ---
st.header("📈 투자 성과 현황")

trades = load_data(TRADE_FILE, [])
costs = load_data(COST_FILE, [])

if not trades.empty:
    display_data = []
    for _, row in trades.iterrows():
        total_buy = row['매수량'] * row['매수단가']
        total_sell = row['매도량'] * row['매도단가']
        profit_amt = total_sell - total_buy
        profit_rate = (profit_amt / total_buy) * 100 if total_buy != 0 else 0
        
        # 이미지와 동일한 2줄 구조 데이터 생성
        display_data.append({
            "종목명": row['종목명'], "구분": "매수", "날짜": row['매수날짜'], 
            "수량": row['매수량'], "단가": f"{row['매수단가']:,}", 
            "총금액": f"{total_buy:,}", "수익금액": f"{profit_amt:,}", "수익률": f"{profit_rate:.1f}%"
        })
        display_data.append({
            "종목명": "", "구분": "매도", "날짜": row['매도날짜'], 
            "수량": row['매도량'], "단가": f"{row['매도단가']:,}", 
            "총금액": f"{total_sell:,}", "수익금액": "", "수익률": ""
        })

    df_display = pd.DataFrame(display_data)
    st.table(df_display) # 이미지와 유사한 깔끔한 표 형식

# --- 요약 섹션 ---
st.divider()
total_trade_profit = 0
if not trades.empty:
    total_trade_profit = (trades['매도량']*trades['매도단가']).sum() - (trades['매수량']*trades['매수단가']).sum()

total_fixed_cost = costs['금액'].sum() if not costs.empty else 0
net_profit = total_trade_profit + total_fixed_cost

c1, c2, c3 = st.columns(3)
c1.metric("누적 매매 수익", f"{total_trade_profit:,.0f}원")
c2.metric("누적 고정비(리딩비)", f"{total_fixed_cost:,.0f}원", delta_color="inverse")
c3.metric("최종 순수익", f"{net_profit:,.0f}원")

if not costs.empty:
    with st.expander("고정비 지출 내역 보기"):
        st.write(costs)