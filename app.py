import streamlit as st

# 1. 頁面基本配置
st.set_page_config(
    page_title="TOYOTA bZ4X 油轉電 AI 智慧購車顧問",
    page_icon="⚡",
    layout="wide"
)

# 嘗試載入繪圖套件
try:
    import pandas as pd
    import plotly.express as px
    has_plotly = True
except ImportError:
    has_plotly = False

# 2. 自訂 CSS 樣式 (包含側邊欄按鈕固定於底部)
st.markdown("""
<style>
/* MBTI 雙色量表文字樣式 */
.mbti-label-disagree {
    color: #88619A;
    font-weight: bold;
    font-size: 14px;
    text-align: right;
    padding-right: 5px;
}
.mbti-label-agree {
    color: #2EA169;
    font-weight: bold;
    font-size: 14px;
    text-align: left;
    padding-left: 5px;
}

/* 置底浮動導覽區塊，確保按鈕不用滑動就能直接點擊 */
[data-testid="stSidebar"] > div:first-child {
    display: flex;
    flex-direction: column;
    height: 100vh;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# 全局狀態初始化 (Session State)
# ------------------------------------------------------------
if "menu" not in st.session_state:
    st.session_state.menu = "4. AI 專屬顧問問答"  # 預設一進去就是 AI 對話

if "diagnosis_submitted" not in st.session_state:
    st.session_state.diagnosis_submitted = False
if "diagnosis_data" not in st.session_state:
    st.session_state.diagnosis_data = None

if "tco_calculated" not in st.session_state:
    st.session_state.tco_calculated = False
if "tco_data" not in st.session_state:
    st.session_state.tco_data = None

if "route_data" not in st.session_state:
    st.session_state.route_data = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "👋 您好！我是您的 bZ4X AI 智慧購車顧問。我可以為您提供專屬的「油轉電適配診斷」、「持有成本試算」與「長途里程模擬」。請隨時點擊左側功能選項或直接與我對話！"}
    ]

# ------------------------------------------------------------
# 3. 側邊欄導覽功能與流程控制按鈕
# ------------------------------------------------------------
st.sidebar.title("🚗 TOYOTA bZ4X")
st.sidebar.subheader("油轉電 AI 智慧購車顧問")
st.sidebar.markdown("---")

# 📌 機能獨立按鈕區塊
st.sidebar.markdown("**📌 功能主選單**")

def render_menu_button(label, target_menu):
    btn_type = "primary" if st.session_state.menu == target_menu else "secondary"
    if st.sidebar.button(label, key=f"btn_nav_{target_menu}", type=btn_type, use_container_width=True):
        st.session_state.menu = target_menu
        st.rerun()

render_menu_button("🤖 4. AI 專屬顧問問答", "4. AI 專屬顧問問答")
render_menu_button("⚡ 1. 油轉電適配度診斷", "1. 適配度診斷")
render_menu_button("💰 2. 總持有成本試算", "2. 持有成本試算")
render_menu_button("🗺️ 3. 長途與天候模擬", "3. 長途情境模擬")

st.sidebar.markdown("---")

# 🔄 上下垂直排列的流程快速切換按鈕（不需滑動即可看到）
st.sidebar.markdown("**🔄 流程快速切換**")

if st.session_state.menu == "4. AI 專屬顧問問答":
    if st.sidebar.button("🚀 開始進行適配度診斷 ⬇️", type="primary", use_container_width=True):
        st.session_state.menu = "1. 適配度診斷"
        st.rerun()

elif st.session_state.menu == "1. 適配度診斷":
    if st.sidebar.button("➡️ 下一步：持有成本試算", type="primary", use_container_width=True):
        st.session_state.menu = "2. 持有成本試算"
        st.rerun()
    if st.sidebar.button("💬 返回 AI 專屬顧問對話", use_container_width=True):
        st.session_state.menu = "4. AI 專屬顧問問答"
        st.rerun()

elif st.session_state.menu == "2. 持有成本試算":
    if st.sidebar.button("➡️ 下一步：長途情境模擬", type="primary", use_container_width=True):
        st.session_state.menu = "3. 長途情境模擬"
        st.rerun()
    if st.sidebar.button("⬅️ 上一步：適配度診斷", use_container_width=True):
        st.session_state.menu = "1. 適配度診斷"
        st.rerun()
    if st.sidebar.button("💬 返回 AI 專屬顧問對話", use_container_width=True):
        st.session_state.menu = "4. AI 專屬顧問問答"
        st.rerun()

elif st.session_state.menu == "3. 長途情境模擬":
    if st.sidebar.button("⬅️ 上一步：持有成本試算", use_container_width=True):
        st.session_state.menu = "2. 持有成本試算"
        st.rerun()
    if st.sidebar.button("💬 返回 AI 專屬顧問對話", type="primary", use_container_width=True):
        st.session_state.menu = "4. AI 專屬顧問問答"
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("💡 提示：所有診斷與試算數據皆會自動整合並回傳給 AI 顧問。")

# ==========================================
# Helper Function: 10 題雙色量表 (不預設選項)
# ==========================================
def render_mbti_question(q_key, q_text):
    st.markdown(f"##### {q_text}")
    options = [1, 2, 3, 4, 5]
    
    col_disagree, col_radio, col_agree = st.columns([2, 3, 2])
    
    with col_disagree:
        st.markdown("<div class='mbti-label-disagree'>1分 (非常不同意)</div>", unsafe_allow_html=True)
    with col_radio:
        selected_score = st.radio(
            q_key,
            options,
            index=None, # 不預設選項
            horizontal=True,
            label_visibility="collapsed"
        )
    with col_agree:
        st.markdown("<div class='mbti-label-agree'>5分 (非常同意)</div>", unsafe_allow_html=True)
        
    st.write("")
    return selected_score

# ==========================================
# 4. AI 專屬顧問問答 (一進來的預設首頁)
# ==========================================
if st.session_state.menu == "4. AI 專屬顧問問答":
    st.title("🤖 4. AI 智慧購車顧問")
    st.caption("即時解答您的換電疑慮，並根據您的分析報告提供客製化建議。")
    st.divider()

    # 顯示目前已完成的測驗數據摘要卡片
    if st.session_state.diagnosis_data or st.session_state.tco_data:
        st.markdown("##### 📋 您目前的分析摘要")
        col_summary1, col_summary2 = st.columns(2)
        with col_summary1:
            if st.session_state.diagnosis_data:
                st.info(f"🎯 **適配指數**：{st.session_state.diagnosis_data['overall_score']} 分")
            else:
                st.warning("🎯 **適配診斷**：尚未完成 (點擊左側開始)")
        with col_summary2:
            if st.session_state.tco_data:
                st.success(f"💰 **省下能源費**：約 ${st.session_state.tco_data['savings']:,.0f} 元")
            else:
                st.warning("💰 **成本試算**：尚未完成 (點擊左側開始)")
        st.divider()

    # 顯示歷史對話紀錄
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # 對話輸入
    if user_input := st.chat_input("請輸入您的疑問（如：保固多久？充電方便嗎？）："):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # AI 思考與整合個人化數據回答
        with st.chat_message("assistant"):
            ai_reply = ""
            
            # 整合適配數據進行個別回應
            score_context = ""
            if st.session_state.diagnosis_data:
                score_context = f"（參考您的適配度分數：{st.session_state.diagnosis_data['overall_score']}分）"

            if "保固" in user_input:
                ai_reply = f"TOYOTA bZ4X 提供原廠大電池 **8 年或 16 萬公里**（以先到者為準）保固，保障容量不低於 70%！{score_context}"
            elif "成本" in user_input or "省多少" in user_input:
                if st.session_state.tco_data:
                    ai_reply = f"根據您剛剛的試算，換開 bZ4X 在 {st.session_state.tco_data['years']} 年內預計能為您省下 **${st.session_state.tco_data['savings']:,.0f} 元** 的燃料開銷！"
                else:
                    ai_reply = "您可以點擊左側選單進行「持有成本試算」，輸入您目前的用車情況，我能精確計算為您省下的燃料費！"
            elif "充電" in user_input or "長途" in user_input:
                ai_reply = f"bZ4X 支援全台快充網絡。在長途駕駛時，使用 DC 快充約 30 分鐘即可充至 80% 電量，正好是休息站喝杯咖啡的時間！{score_context}"
            else:
                ai_reply = f"針對『{user_input}』{score_context}，TOYOTA 提供全台密集的展示中心與維護據點。建議您可以直接預約試駕，體驗純電車帶來的安靜與順暢加速感！"

            st.write(ai_reply)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})

# ==========================================
# 1. 適配度診斷
# ==========================================
elif st.session_state.menu == "1. 適配度診斷":
    if not st.session_state.diagnosis_submitted:
        st.title("⚡ 1. 油轉電適配度診斷")
        st.write("請依據您的實際用車習慣點選分數 (1分最低，5分最高)，填寫完畢後點擊下方『送出診斷』：")
        st.divider()

        with st.form("diagnosis_form"):
            q1 = render_mbti_question("q1", "Q1. 我家或工作地點有固定車位，且具備安裝充電設備的條件")
            q2 = render_mbti_question("q2", "Q2. 長途駕駛時，我習慣停靠休息站 20-30 分鐘喝咖啡/上廁所並順便補電")
            q3 = render_mbti_question("q3", "Q3. 我平日單日開車總里程多在 80 公里以內，如市區通勤與接送")
            q4 = render_mbti_question("q4", "Q4. 我非常渴望降低每個月的油資開銷與長期車輛保養維修費用")
            q5 = render_mbti_question("q5", "Q5. 我非常期待純電車帶來的瞬間加速流暢感與安靜無噪音的駕馭體驗")
            q6 = render_mbti_question("q6", "Q6. 購買電動車時，我更看重車廠的全台服務據點密度與售後保固保障")
            q7 = render_mbti_question("q7", "Q7. 我能接受在出發長途跨縣市旅遊前，先用手機 App 規劃順路充電站")
            q8 = render_mbti_question("q8", "Q8. 我買車主要用於家庭日常出遊、載人載物，對車室空間與舒適度要求高")
            q9 = render_mbti_question("q9", "Q9. 我喜歡嘗試智慧駕駛輔助系統 (如 TSS 3.0) 與遠端車輛控制科技")
            q10 = render_mbti_question("q10", "Q10. 我認為電動車是未來趨勢，並願意在 1-2 年內嘗試換購純電動車")

            submitted = st.form_submit_button("🚀 送出診斷，查看分析結果", type="primary", use_container_width=True)

            if submitted:
                all_answers = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10]
                if None in all_answers:
                    st.error("⚠️ 請完成所有題目評分後再送出！")
                else:
                    weighted_score = (
                        q1 * 0.15 + q2 * 0.12 + q3 * 0.12 + q4 * 0.12 + q5 * 0.10 +
                        q6 * 0.10 + q7 * 0.08 + q8 * 0.08 + q9 * 0.08 + q10 * 0.05
                    )
                    overall_score = int((weighted_score / 5.0) * 100)

                    dim_charging = (q1 * 0.15 + q2 * 0.12) / 0.27
                    dim_range = (q3 * 0.12 + q7 * 0.08) / 0.20
                    dim_cost = (q4 * 0.12) / 0.12
                    dim_trust = (q5 * 0.10 + q6 * 0.10 + q9 * 0.08) / 0.28
                    dim_lifestyle = (q8 * 0.08 + q10 * 0.05) / 0.13

                    st.session_state.diagnosis_data = {
                        "overall_score": overall_score,
                        "categories": ['充電便利', '里程規劃', '經濟效益', '駕馭信任', '空間意願'],
                        "values": [dim_charging, dim_range, dim_cost, dim_trust, dim_lifestyle]
                    }
                    st.session_state.diagnosis_submitted = True
                    
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"📊 【系統自動更新】使用者已完成「適配度診斷」！得分為 **{overall_score} 分**。已將五大維度分數紀錄入分析檔案。"
                    })
                    st.rerun()

    else:
        data = st.session_state.diagnosis_data

        st.title("🎯 您的 TOYOTA bZ4X 油轉電專屬診斷報告")
        st.caption("基於您的 10 項用車習慣與生活型態問卷加權分析結果")
        st.divider()

        col_left, col_right = st.columns([4, 6], gap="large")

        with col_left:
            st.subheader("📊 總體適配評分")
            st.metric(label="bZ4X 油轉電適配指數", value=f"{data['overall_score']} / 100 分")
            st.progress(data['overall_score'] / 100)
            
            st.markdown("---")
            st.subheader("💡 AI 購車建議")
            if data['overall_score'] >= 80:
                st.success("🎉 **高度適合！** 您具備極佳的電動車使用條件與心態，TOYOTA bZ4X 能為您帶來大幅降低的持有成本與極佳駕馭體驗。")
            elif data['overall_score'] >= 60:
                st.info("👍 **相當適合！** 您非常適合入手 bZ4X，僅需在長途旅遊前稍微建立規劃充電站的習慣，即可輕鬆享受純電生活。")
            else:
                st.warning("⚠️ **建議評估！** 您的生活情境可能目前較缺乏固定充電條件，建議可先體驗試駕，或透過本系統的「長途情境模擬」進行進一步評估。")

            st.write("")
            if st.button("🔄 重新進行適配度診斷", use_container_width=True):
                st.session_state.diagnosis_submitted = False
                st.session_state.diagnosis_data = None
                st.rerun()

        with col_right:
            st.subheader("🕸️ 5 大維度分析雷達圖")
            if has_plotly:
                df_radar = pd.DataFrame(dict(
                    r=data['values'],
                    theta=data['categories']
                ))

                fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True, range_r=[0, 5])
                fig.update_traces(fill='toself', line_color='#2EA169')
                
                # 縮小高度與優化邊距，隱藏右上工具列
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 5])
                    ),
                    showlegend=False,
                    height=350,
                    margin=dict(l=60, r=60, t=40, b=40)
                )

                st.plotly_chart(
                    fig, 
                    use_container_width=True, 
                    config={'displayModeBar': False}
                )
            else:
                st.error("⚠️ 請在 Terminal 輸入 `pip install pandas plotly` 以啟用雷達圖！")

# ==========================================
# 2. 持有成本試算
# ==========================================
elif st.session_state.menu == "2. 持有成本試算":
    st.title("💰 2. 總持有成本 (TCO) 試算")
    st.write("計算換購 TOYOTA bZ4X 後，長期能為您省下的燃料與維護開銷。")
    st.divider()

    # 車型資料庫 (快速填入預設值)
    car_db = {
        "自訂輸入": {"mpg": 0.0, "fuel_type": "95 無鉛"},
        "Toyota Corolla Cross 1.8 汽油": {"mpg": 14.9, "fuel_type": "95 無鉛"},
        "Toyota RAV4 2.0 汽油": {"mpg": 15.3, "fuel_type": "95 無鉛"},
        "Honda CR-V 1.5T": {"mpg": 14.7, "fuel_type": "95 無鉛"},
        "Ford Kuga 1.5T": {"mpg": 15.0, "fuel_type": "95 無鉛"},
        "Nissan Kicks 1.6": {"mpg": 16.0, "fuel_type": "95 無鉛"}
    }

    selected_car = st.selectbox("🚗 快速選擇您目前的車款（自動載入資料庫油耗）：", list(car_db.keys()))
    default_mpg = car_db[selected_car]["mpg"]

    # 表單預設值為 0
    with st.form("tco_form"):
        col1, col2 = st.columns(2)
        with col1:
            annual_km = st.number_input("預估年行駛里程 (公里)：", min_value=0, value=0, step=1000)
            gas_price = st.number_input("平均油價 (元/公升)：", min_value=0.0, value=0.0, step=0.5)
            gas_km = st.number_input(
                "目前油車平均油耗 (公里/公升)：", 
                min_value=0.0, 
                value=float(default_mpg), 
                help="選取預設車款會自動帶入平均油耗"
            )
        
        with col2:
            electricity_price = st.number_input("電車平均電費 (元/度)：", min_value=0.0, value=0.0, step=0.5)
            years = st.slider("計算年限 (年)：", 1, 10, 5)

        tco_submitted = st.form_submit_button("🚀 開始計算省下金額", type="primary", use_container_width=True)

    if tco_submitted:
        if annual_km == 0 or gas_price == 0 or gas_km == 0 or electricity_price == 0:
            st.warning("⚠️ 請填寫完整的試算參數（數值需大於 0）！")
        else:
            annual_gas = (annual_km / gas_km) * gas_price
            annual_ev = (annual_km / 6.0) * electricity_price
            savings = (annual_gas - annual_ev) * years

            st.session_state.tco_data = {
                "savings": savings,
                "years": years
            }
            st.session_state.tco_calculated = True

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"💰 【系統自動更新】使用者已完成「持有成本試算」！預計 {years} 年內可省下 **${savings:,.0f} 元** 能源開銷。"
            })

    if st.session_state.tco_calculated and st.session_state.tco_data:
        st.divider()
        savings_val = st.session_state.tco_data['savings']
        years_val = st.session_state.tco_data['years']
        st.success(f"🎉 預計在 {years_val} 年內，換開 TOYOTA bZ4X 可為您省下約 **${savings_val:,.0f} 元** 的燃料開銷！")

# ==========================================
# 3. 長途情境模擬
# ==========================================
elif st.session_state.menu == "3. 長途情境模擬":
    st.title("🗺️ 3. 車主長途與不同氣候情境模擬")
    st.write("自訂旅程起終點與極端天候條件，評估 bZ4X 的實際里程與補電規劃。")
    st.divider()

    col_input1, col_input2 = st.columns(2)
    with col_input1:
        origin = st.text_input("📍 出發地址 / 地點：", value="台北車站")
        destination = st.text_input("🏁 目的地址 / 地點：", value="高雄左營高鐵站")
        estimated_dist = st.number_input("估算單程總里程 (公里)：", min_value=10, value=350, step=10)

    with col_input2:
        season = st.selectbox("🌤️ 季節與氣溫：", ["夏季酷暑 (空調全開 24°C)", "舒適春秋 (22°C-26°C)", "冬季寒流 (開啟暖氣/座椅加熱)"])
        weather = st.selectbox("🌧️️ 天氣與風雨：", ["晴天順風", "豪雨/積水 (增加滾動阻力)", "颱風暴風雨 (強陣風阻)"])

    if st.button("🚀 開始計算行程與充電規劃", type="primary", use_container_width=True):
        base_range = 400
        penalty = 1.0

        if "酷暑" in season: penalty *= 0.9
        elif "寒流" in season: penalty *= 0.85

        if "豪雨" in weather: penalty *= 0.88
        elif "颱風" in weather: penalty *= 0.80

        real_range = int(base_range * penalty)
        battery_consume_pct = int((estimated_dist / real_range) * 100)

        st.divider()
        st.subheader("📊 模擬分析結果")

        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric("真實環境可用續航", f"{real_range} km", delta=f"{int((penalty-1)*100)}% 環境影響")
        with col_res2:
            st.metric("預估消耗電量", f"{battery_consume_pct} %")
        with col_res3:
            stops_needed = 0 if battery_consume_pct < 80 else (1 if battery_consume_pct < 150 else 2)
            st.metric("建議中途補電次數", f"{stops_needed} 次")

        st.markdown("---")
        st.markdown("##### 📍 AI 建議補電規劃路線")
        if battery_consume_pct < 80:
            st.success(f"✅ 從 **{origin}** 至 **{destination}** 全程不需中途充電，抵達目的地後剩餘電量約 {100 - battery_consume_pct}%！")
        else:
            st.warning(f"⚠️ 受環境氣候影響電耗較高，建議於途中停靠 **TOYOTA 國道高速公路展間/休息站快充站** 補電 20 分鐘即可順利抵達！")

        st.session_state.route_data = {
            "origin": origin,
            "destination": destination,
            "dist": estimated_dist,
            "weather": f"{season} / {weather}"
        }
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"🗺️ 【系統自動更新】使用者已完成「路線模擬」！從 {origin} 至 {destination}（{estimated_dist}km），在 {season}、{weather} 下進行了評估。"
        })
