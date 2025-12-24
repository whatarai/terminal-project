1.程式的功能與技術原理
這個程式是一個互動式的化學反應模擬平台，支援以下五種核心反應類型：基礎反應：零級 (Zero-order)、一級 (First-order)、二級 (Second-order) 反應。複合反應：連串反應 (Consecutive)、平行反應 (Parallel)。我在程式中求數值時捨棄現成的 SciPy 函式庫，改用 NumPy 手寫實作 四階龍格－庫塔法 (RK4)。RK4的數學邏輯是透過在每一個時間步長 (dt) 內進行四次斜率（導數）採樣，並進行加權平均，將截斷誤差降低。使得模擬曲線在處理非線性（如二級反應）或剛性系統（如連串反應）時，能保持極高的穩定性與精確度。最後是AI 數據診斷：整合 Google Gemini 1.5 Flash 大型語言模型，實現從「模擬數據」到「專業解釋」的自動化流程。
2.使用方式
在終端安裝必要套件：Bashpip install streamlit numpy matplotlib google-generativeai
啟動程式：python3 -m streamlit run pro.py
操作流程：在左側邊欄選單切換 反應級數。調整滑桿設定 速率常數 (k)、初始濃度 與 運算步長 (dt)。在下方 API 設定區輸入金鑰，點擊「生成分析報告」獲取數據見解。
3.程式架構
get_derivatives(): 物理建模模組，定義各類反應的微分方程組。solve_rk4(): 核心運算引擎，執行 NumPy 矩陣迭代。Streamlit UI: 提供即時互動介面與 Matplotlib 圖表渲染。Fallback 模組: 當雲端 API 發生 404 報錯或網路異常時，自動觸發本地數據診斷邏輯。
4.開發過程
首先就是API 404 報錯：開發過程中發現 Google API 端點版本 (v1beta) 頻繁變動，導致 gemini-1.5-flash 偶發性無法連線。最後新增了本地的分析，也就是列出運算後的結果，讓就算python套件版本與模型名稱不匹配，或是 API 版本設定有問題，程式還能運行下去。再來還有數值不穩定，原本使用scipy運算時，在二級反應中，若步長設定不當，濃度會出現負值或發散。解決方式就是用更精確的 RK4演算法取代簡易歐拉法，有效解決數值發散問題。
5.參考資料來源
參考：gemini rk4運算參考網站：https://physexp.thu.edu.tw/~AP/YC/NUM/HTML/NUM-planetary-rk4-lec.html 反應速率程式的靈感來自於這個使用excel的製圖：http://science4everyone.net/MediaWiki/index.php?title=%E4%BB%A5Excel%E7%A8%8B%E5%BC%8F%E6%A8%A1%E6%93%AC%E5%8F%8D%E6%87%89%E9%80%9F%E7%8E%87
6.程式修改與增強內容 
本程式中使用的rk4運算是由我提出且也是我編的，llm提供的幫助主要是幫我檢查跟修改bug，我對於建立頁面與側邊欄並不熟悉，所以這部分是由gemini負責，而我負責用課程中學到的matplotlib繪圖功能實現顯示濃度曲線的效果。
