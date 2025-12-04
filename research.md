# **包容性節奏：建構視障優先的智慧型鼓譜教學 Web 應用程式研究報告**

## **執行摘要**

在音樂教育科技的快速發展中，無障礙設計往往是事後補救而非核心架構。儘管數位音樂工具（如 DAW、數位樂譜軟體）日益普及，但其高度依賴視覺介面（Visual Paradigms）——如波形圖、鋼琴捲簾（Piano Roll）及標準五線譜——這對全球估計超過 22 億的視力受損人士造成了巨大的學習門檻。本報告旨在回應一項具體的技術需求：開發一個基於 Web 的應用程式，允許用戶上傳鼓譜（PDF 或圖片），通過光學樂譜識別（OMR）與專家系統（Expert System）進行分析，並透過語音合成（TTS）技術以「視障優先」（Accessibility-First）的設計理念教導使用者打鼓。

本研究報告深入探討了實現此系統所需的端到端技術架構。從電腦視覺的角度，我們分析了針對打擊樂譜特有的 OMR 挑戰，包括非音高符號（Unpitched Notation）的識別與多聲部（Polyphonic）節奏的解構。在專家系統層面，我們提出了基於規則的演算法來解析 MusicXML，並利用數學複雜度度量（如 Lempel-Ziv 複雜度）來自動生成教學腳本。在互動設計層面，報告詳細闡述了如何利用 Web Speech API 與 Web Audio API 實現高精度的視聽同步，並結合 WAI-ARIA 標準與聽覺圖標（Earcons）來構建無需視覺輔助的導航體驗。

這不僅僅是一個樂譜閱讀器，而是一個「虛擬導師」。它將靜態的視覺圖像轉化為動態的、結構化的語音指令，模擬人類教師的教學邏輯，將複雜的肢體協調動作分解為可執行的單元。本報告將分為七個主要章節，全面剖析從底層演算法到上層使用者體驗的每一個關鍵環節。

## ---

**1\. 導論：打破音樂教育的視覺霸權**

### **1.1 視障音樂家的學習困境**

西方音樂記譜法（Western Musical Notation）本質上是一種圖形語言。它利用二維空間來編碼聲音資訊：垂直軸代表音高，水平軸代表時間。對於明眼音樂家而言，樂譜提供了一種「格式塔」（Gestalt）式的認知優勢，能夠一眼識別出旋律輪廓或節奏型態。然而，對於視障音樂家，這種同步獲取資訊的途徑被切斷了。

傳統的替代方案，如布點樂譜（Braille Music），雖然是一套國際公認的嚴謹標準，但其線性閱讀的特性要求使用者必須先用手指「閱讀」並記憶一段音樂，然後才能騰出手來在樂器上演奏，這極大地阻礙了視奏（Sight-reading）的流暢性 1。此外，布點樂譜的學習曲線極其陡峭，且製作成本高昂，這使得大量僅以 PDF 或圖片形式存在的現代鼓譜資源對於視障者來說是不可觸及的 2。

### **1.2 鼓譜的特殊性與挑戰**

打擊樂記譜法與旋律樂器（如鋼琴、小提琴）截然不同，這為自動化識別與教學帶來了獨特的挑戰。

1. **非音高映射（Unpitched Mapping）：** 鼓譜上的位置並不代表頻率，而是代表物理樂器。例如，五線譜的下加一間通常代表大鼓（Bass Drum），第三間代表小鼓（Snare Drum）。然而，這種映射並非絕對標準化，不同的出版社可能對中鼓（Toms）或鈸（Cymbals）有不同的位置定義 3。  
2. **符號形態學（Symbol Morphology）：** 為了區分鼓皮（Membranes）與金屬鈸（Idiophones），鼓譜大量使用不同的符頭形狀。標準的橢圓形音符通常代表鼓，而「X」形音符則代表鈸（Hi-Hat, Ride, Crash）。此外，還有代表「鬼音」（Ghost Notes）的括號、代表開鈸（Open Hi-Hat）的圓圈等。OMR 系統必須具備極高的形態區分能力，因為混淆一個實心點和一個 X，就等於混淆了小鼓與銅鈸，完全改變了音樂語意 5。  
3. **多肢體並行（Limb Independence）：** 鼓譜通常是單行多聲部的。一個標準的搖滾節奏可能包含三層資訊流：右手在 Hi-Hat 上的固定音型，左手在 Snare 上的後拍（Backbeat），以及右腳在 Bass Drum 上的切分音（Syncopation）。視障學生需要的不是簡單的 MIDI 播放，而是關於「哪隻手打哪個樂器」的具體指導 7。

### **1.3 「原生無障礙」（Born-Accessible）的系統願景**

本專案的目標是建立一個「原生無障礙」的 Web 應用。這意味著無障礙不是在開發後期添加的 ARIA 標籤，而是從系統架構的底層就考慮非視覺交互。

* **輸入端：** 支援標準視覺格式（PDF/JPG），利用 AI 代理視障者的眼睛。  
* **處理端：** 專家系統不僅解析音符，更解析「演奏邏輯」（Stickings and Limb Assignment）。  
* **輸出端：** 利用高精度的 TTS 技術，提供分層次的、音樂性的語音指導，並輔以聽覺圖標（Earcons）進行介面導航 8。

## ---

**2\. 針對打擊樂的光學樂譜識別 (OMR) 技術架構**

光學樂譜識別（OMR）是本系統的感知層。傳統的 OMR 系統（如 PhotoScore, SmartScore）在處理打擊樂譜時往往表現不佳，因為它們主要是為旋律樂器設計的。為了實現高精度的鼓譜識別，我們需要採用基於深度學習的現代架構，並針對打擊樂符號進行專門的訓練與微調。

### **2.1 圖像預處理與增強 (Image Preprocessing)**

使用者上傳的樂譜圖片品質可能參差不齊（如手機拍攝的彎曲、陰影、低解析度）。在進入神經網絡之前，必須進行嚴格的預處理。

#### **2.1.1 糾偏與去噪 (Deskewing and Binarization)**

* **糾偏（Deskewing）：** 鼓譜的垂直位置決定了樂器種類。如果圖片傾斜，演算法可能會將位於第三間的小鼓誤判為第三線的中鼓。利用霍夫變換（Hough Transform）或基於投影剖面（Projection Profile）的方法可以檢測五線譜的水平線，並計算旋轉角度 $\\theta$ 進行校正 9。  
* **二值化（Binarization）：** 為了分離前景符號與背景噪聲，應採用自適應閾值法（如 Sauvola 演算法），這比全局閾值更能應對光照不均的情況。  
* **五線譜線處理：** 傳統方法傾向於移除譜線以隔離符號，但這容易破壞音符結構（如斷裂的符桿）。現代端到端（End-to-End）模型通常保留譜線，利用譜線作為垂直坐標的參考系，這對於確定打擊樂器位置至關重要 10。

### **2.2 深度學習模型的選擇：TrOMR 與 YOLO 的權衡**

目前學術界在 OMR 領域主要有兩大流派：基於序列的轉換器模型（Transformers）和基於物件的檢測模型（Object Detectors）。

#### **2.2.1 基於 Transformer 的序列建模 (TrOMR)**

**TrOMR**（Transformer-based Optical Music Recognition）將樂譜識別視為圖像到序列（Image-to-Sequence）的翻譯問題，類似於 NLP 中的機器翻譯 10。

* **架構：** 使用 ResNet 作為編碼器提取特徵，Transformer 作為解碼器生成符號序列（例如：clef-percussion, note-F4\_eighth, barline）。  
* **優勢：** Transformer 擅長捕捉全局上下文依賴關係。例如，它能理解小節線（Barline）與拍號（Time Signature）之間的關係，或者重複記號（Repeat Sign）的語意。  
* **劣勢：** 對於垂直密度極高的鼓譜（例如：同一拍子上同時出現 Hi-Hat, Snare, Bass Drum），序列化輸出可能產生歧義。模型需要學習特定的閱讀順序（通常是從上到下或從下到上）10。

#### **2.2.2 基於 YOLO 的物件檢測 (YOLOv8)**

**YOLO**（You Only Look Once）將樂譜符號視為獨立的物件進行檢測 12。

* **架構：** 單階段檢測器，直接預測邊界框（Bounding Box）和類別概率。  
* **針對鼓譜的優勢：** YOLO 非常適合檢測微小且形態各異的符號。我們可以訓練特定的類別，如 notehead-black（實心符頭）、notehead-x（交叉符頭）、symbol-open（開鈸圈）、symbol-ghost（鬼音括號）。這解決了傳統 OMR 難以區分鈸與鼓的問題。  
* **挑戰：** YOLO 輸出的只是一堆雜亂的框。需要一個後處理步驟（Notation Assembly）來將「符頭」、「符桿」和「符尾」組裝成有意義的音符，並根據其在五線譜上的相對位置確定樂器 13。

#### **2.2.3 推薦架構：混合專家模型**

考慮到鼓譜的特殊性，本報告建議採用 **混合架構**：

1. 利用 **YOLOv8** 進行精確的符號檢測（Symbol Detection），特別是區分各種特殊的符頭和裝飾音（Flam, Drag, Accents），因為這些對於捕捉「律動」（Groove）至關重要 14。  
2. 利用 **圖神經網絡（Graph Neural Networks, GNN）** 或啟發式算法進行符號組裝（Notation Assembly），將檢測到的符頭與譜線位置結合，生成語意化的音樂圖（Music Notation Graph, MuNG）16。

### **2.3 訓練數據集的構建策略**

現有的 OMR 數據集（如 MUSCIMA++）多側重於古典樂或手寫樂譜，缺乏打擊樂特有的符號分佈 17。為了訓練高精度的鼓譜識別模型，必須構建專用數據集。

| 數據集名稱 | 類型 | 適用性分析 | 引用來源 |
| :---- | :---- | :---- | :---- |
| **DeepScoresV2** | 合成/印刷體 | 包含大量微小音樂符號及多樣化的記譜，適合做預訓練（Pre-training）以學習基礎形狀。 | 17 |
| **MUSCIMA++** | 手寫體 | 提供手寫樂譜的標註，有助於提高模型對用戶手寫鼓譜的魯棒性。 | 17 |
| **Simulated Drum Dataset** | 合成 (Python) | **關鍵策略：** 使用 Python 腳本（結合 LilyPond 或 MuseScore CLI）自動生成數百萬張帶有完美標籤（Ground Truth）的鼓譜圖片。我們可以窮舉各種節奏組合、切分音型態及樂器配置，訓練模型識別複雜的多聲部鼓譜。 | 19 |

**數據增強（Data Augmentation）：** 為了模擬真實應用場景，訓練數據必須經過彈性變形（Elastic Distortion）、模糊（Blur）、光照梯度模擬（Lighting Gradient）及噪聲添加，以確保模型能處理手機拍攝的低質量圖片 21。

## ---

**3\. 專家系統：從符號到教學法的語意轉譯**

OMR 的輸出通常是 MusicXML 或 MIDI，這對視障初學者來說仍然過於抽象。**專家系統（Expert System）** 的核心任務是充當「虛擬教練」，解析這些符號數據，轉化為符合認知心理學的教學指令。

### **3.1 MusicXML 的深度解析與標準化**

MusicXML 是本系統的中介格式，但其對打擊樂的描述相當繁瑣。

XML

\<note\>  
  \<unpitched\>  
    \<display-step\>G\</display-step\>  
    \<display-octave\>5\</display-octave\>  
  \</unpitched\>  
  \<notehead\>x\</notehead\>  
  \<instrument id\="P1-I3"/\>  
\</note\>

專家系統必須解析 \<unpitched\> 標籤中的 display-step（位置）與 notehead（形狀），並結合 \<instrument\> 定義來推斷實際樂器 22。

* **樂器映射演算法（Instrument Mapping Algorithm）：** 系統需內建一套啟發式規則庫（Heuristic Rule Base）。例如：「若音符位於五線譜上加一間且符頭為 X，則 95% 機率為 Hi-Hat；若有圓圈標記則為 Open Hi-Hat」4。對於非標準記譜，系統應通過 TTS 詢問用戶：「檢測到非常規位置的音符，請問這是 Cowbell 還是 Ride Bell？」

### **3.2 肢體分配與運動學分析 (Limb Assignment)**

盲人學習打鼓最大的障礙在於無法模仿老師的動作。系統必須通過演算法自動分配肢體（Stickings）。

* **規則引擎：**  
  1. **頻率規則：** 高頻率、持續的節奏（Ostinato，如 8 分音符的 Hi-Hat）通常分配給 **右手**（對於右撇子）。  
  2. **重音規則：** 小鼓的後拍（Backbeat，通常在第 2、4 拍）分配給 **左手**。  
  3. **低音規則：** 符桿朝下或位於底部的音符（大鼓）分配給 **右腳**；Hi-Hat 踏板分配給 **左腳** 5。  
  4. **線性分析：** 對於快速過門（Fills），系統應計算最佳的左右手交替邏輯（如 RLRL），避免「交叉手」（Cross-sticking）造成的物理打結，除非是特定的演奏技巧 19。

### **3.3 節奏複雜度分析與分塊教學 (Chunking Strategy)**

為了避免資訊過載（Cognitive Overload），系統不能一次性唸出一整首曲子。專家系統需計算樂譜的 **節奏複雜度**，將其分割為可管理的「學習塊」（Chunks）。

* **Lempel-Ziv 複雜度 (LZC)：** 這是一種資訊理論度量，用於計算序列中的重複模式 24。如果一段鼓譜的 LZC 值較低，表示其具有高度重複性（如標準 Rock Beat），系統可以指示：「這是一個重複 4 次的小節」。如果 LZC 值高（如變奏或過門），系統則會切換到「逐拍教學模式」。  
* **切分音度量 (Syncopation Measures)：** 利用 **加權音符-拍點距離 (Weighted Note-to-Beat Distance, WNBD)** 演算法計算切分程度 25。對於 WNBD 值高的小節，TTS 應自動放慢語速，並採用更細分的計數方式（如 "1-e-and-a" 而非 "1-2-3-4"）。

### **3.4 風格與律動識別 (Groove Classification)**

單純的量化播放聽起來像機器人。專家系統應分析大鼓與小鼓的交互模式，識別音樂風格（如 Swing, Funk, Bossa Nova）26。

* **應用場景：** 若識別為 "Swing"，TTS 會提示：「請注意，這裡的八分音符需要帶有三連音的搖擺感（Shuffle feel）。」這對於視障者掌握樂曲的「氣質」至關重要。

## ---

**4\. 聽覺使用者介面 (AUI) 與語音教學設計**

這是本系統與使用者的接觸面。設計必須遵循「聽覺優先」原則，提供清晰、無歧義且具音樂性的導航與教學。

### **4.1 節奏模式的口語化描述 (Verbalization)**

如何「唸」出節奏是一門科學。簡單地唸出音符名稱（"大鼓、小鼓、大鼓"）缺乏時間感。系統應提供多種描述模式：

1. **網格描述法 (The Grid Method)：** 基於公制網格的精確描述。  
   * *Script:* "第一拍打大鼓。第一拍的後半拍（And）打 Hi-Hat。第二拍打小鼓。"  
   * *優點：* 精確，適合構建堅實的樂理基礎。  
2. **擬聲法 (Mnemonics/Onomatopoeia)：** 模仿鼓聲的口訣，這在認知心理學中被證明能增強運動記憶 27。  
   * *Script:* "Boom \- Ts \- Ka \- Ts"（對應 Kick \- Hat \- Snare \- Hat）。  
   * *實作：* 系統應內建一套音素映射表（Phoneme Map），將 MIDI 事件轉換為語音字串，並通過 TTS 朗讀。  
3. **分層教學法 (Hierarchical Description)：** 模擬人類老師的教學順序。  
   * *Step 1:* "我們先練習右手的 Hi-Hat 模式：連續的八分音符。"  
   * *Step 2:* "現在加入左手，在第二和第四拍打小鼓。"  
   * *Step 3:* "最後，在第一拍和第三拍後半加入大鼓。"

### **4.2 文字轉語音 (TTS) 的技術實作**

* **Web Speech API (speechSynthesis)：** 這是瀏覽器內建的 API，優點是零延遲、無需網路。適合用於介面導航（如「上一小節」、「播放」）28。  
* **雲端神經網絡 TTS (Neural TTS)：** 對於長段落的教學解說，建議使用 Google Cloud TTS 或 Amazon Polly，因為它們的語調（Prosody）更自然，減少聽覺疲勞。  
* **SSML (Speech Synthesis Markup Language)：** 為了讓 TTS 聽起來像音樂老師而非導航儀，必須動態生成 SSML 標籤。  
  * \<break time="500ms"/\>：在樂句之間插入呼吸感。  
  * \<prosody rate="slow"\>：在描述複雜的 Fill-in 時自動放慢語速 30。  
  * \<prosody pitch="+10%"\>：用音高變化來強調重音（Accents）。

### **4.3 高精度視聽同步 (Audio-Visual Synchronization)**

這是一個技術難點。瀏覽器的 TTS 與 Web Audio API 的時鐘通常不同步。

* **解決方案：** 使用 **Web Audio API** 的 AudioContext.currentTime 作為全域主時鐘（Master Clock）31。  
* **預先排程 (Lookahead Scheduling)：** 利用 **Tone.js** 的 Transport 系統，將 TTS 的觸發事件視為一個樂器事件，提前 100ms 進行排程，以補償 JavaScript 的執行延遲 33。  
* **時間戳記映射：** 透過 AudioContext.getOutputTimestamp() 獲取精確的播放時間，將其與 React 前端狀態（Cursor Position）綁定，確保當語音唸到 "第三拍" 時，視覺上的高亮游標（針對低視能者）也剛好移動到第三拍 34。

## ---

**5\. 技術實作策略與開發棧**

### **5.1 前端架構 (Frontend)**

* **框架：** React.js。其組件化架構非常適合管理複雜的樂譜狀態。  
* **樂譜渲染：** **OpenSheetMusicDisplay (OSMD)**。這是目前 Web 端渲染 MusicXML 的標準庫。  
  * *無障礙改造：* OSMD 預設使用 Canvas 渲染，對螢幕閱讀器不可見。我們必須構建一個 **Shadow DOM** 或平行的 HTML 結構（如隱藏的 \<ul\> 列表），將樂譜結構語意化，讓 NVDA 或 VoiceOver 能夠遍歷樂譜內容 35。  
* **狀態管理：** Redux 或 React Context，用於存儲「樂譜數據模型」（Score Model），這是 OMR 解析後的單一事實來源（Single Source of Truth）。

### **5.2 後端架構 (Backend)**

* **語言/框架：** Python (FastAPI)。Python 是 AI/ML 的首選語言。  
* **OMR 服務：** 部署 PyTorch 模型（TrOMR/YOLO）。  
* **處理流程：**  
  1. 圖片上傳 \-\> OpenCV 預處理（糾偏、裁切）。  
  2. 模型推論 \-\> 符號列表。  
  3. 符號組裝 (Symbol Assembly) \-\> MusicXML。  
  4. 專家系統分析 (Expert Analysis) \-\> 生成包含教學元數據（Metadata）的 JSON（如：難度係數、肢體建議、TTS 腳本）。

### **5.3 音訊引擎 (Audio Engine)**

* **核心庫：** **Tone.js**。它是 Web Audio API 的高級封裝，提供了強大的排程器（Scheduler）和採樣器（Sampler）37。  
* **採樣管理：** 預加載高品質的鼓組採樣（Kick, Snare, Hats），確保播放時的聲音真實度，這對聽覺學習至關重要。

### **5.4 互動式「音訊刷動」(Audio Scrubbing)**

這是本應用的一大創新。傳統軟體用滑鼠拖動進度條（Scrubbing），視障者需要類似的機制。

* **鍵盤導航：** 使用左右方向鍵，以「音符」為單位移動。  
* **聽覺反饋：** 每按一次方向鍵，系統播放該位置的鼓聲，並朗讀位置（"小節 3，第 2 拍"）。  
* **WAI-ARIA 模式：** 該控制器應實作為一個 role="slider" 的元件，並動態更新 aria-valuenow 和 aria-valuetext（例如："Measure 3 Beat 2"），以便螢幕閱讀器即時朗讀 39。

## ---

**6\. 使用者介面設計與無障礙標準**

設計必須嚴格遵循 WCAG 2.1 AAA 標準，這是針對特殊需求應用的最高標準 41。

### **6.1 聽覺圖標與導航 (Earcons & Navigation)**

為了減少語音的干擾，系統應大量使用 **聽覺圖標（Earcons）** ——具有抽象意義的短音效 8。

* **小節邊界：** 當使用者導航跨過小節線時，播放一個低沈的 "Thud" 聲。  
* **段落邊界：** 進入副歌（Chorus）或新的段落時，播放一個清脆的 "Ping" 聲。  
* **空間音訊 (Spatial Audio)：** 利用立體聲平移（Panning），將關於左手的指令（小鼓）放在左聲道，右手的指令（Hi-Hat）放在右聲道，利用聽覺空間感輔助肢體定位 43。

### **6.2 針對低視能者的視覺設計**

並非所有視障者都是全盲，許多人保有剩餘視力（Low Vision）。

* **高對比模式：** 提供反色顯示（黑底白符），減少眩光 21。  
* **游標追蹤：** 視覺游標必須加粗、高亮（如鮮黃色），並始終保持在螢幕中央（Auto-scroll），減少眼球掃描的負擔。  
* **向量縮放：** 由於使用 OSMD (SVG)，樂譜可無損放大至 400% 以上而不失真 45。

### **6.3 鍵盤操作邏輯**

完全摒棄滑鼠依賴。建立合乎邏輯的 Tab 順序（Tab Order）：

1. **Skip Links:** "跳至播放器"、"跳至樂譜區域"。  
2. **快捷鍵：**  
   * Space: 播放/暫停。  
   * Left/Right: 上一個/下一個音符。  
   * Up/Down: 上一小節/下一小節。  
   * S: 減速 (Slower)。  
   * F: 加速 (Faster)。  
   * V: 切換語音模式（詳細/簡略/擬聲）。

## ---

**7\. 結論與未來展望**

本研究報告提出了一個整合 OMR、專家系統與 TTS 技術的綜合解決方案，旨在解決視障人士學習打擊樂的痛點。透過將視覺樂譜轉化為結構化的、語意豐富的聽覺體驗，我們不僅僅是提供了一個工具，而是創造了一種新的教學媒介。

**核心創新點總結：**

1. **混合式 OMR 架構：** 結合 TrOMR 的上下文理解與 YOLO 的微小符號檢測，解決鼓譜識別難題。  
2. **語意轉譯層：** 專家系統將 XML 數據轉化為符合人類認知的「肢體指令」與「節奏口訣」。  
3. **聽覺互動範式：** 利用 Earcons 與 Spatial Audio 建立無需視覺的導航與空間感知體系。

**未來發展建議：**

* **觸覺反饋 (Haptic Feedback)：** 整合 Web Bluetooth API，連接穿戴式節拍器（如 Soundbrenner），將節拍轉化為振動，釋放聽覺通道專注於語音指令 46。  
* **即時評估 (Real-Time Assessment)：** 利用 Web Audio 的 AudioWorklet 即時分析用戶的麥克風輸入，比對節奏準確度，並給出語音反饋（"你的小鼓搶拍了"）47。

這套系統的開發將是從「技術輔助」邁向「技術賦能」的重要一步，讓節奏的學習不再受限於視力，而是回歸音樂最本質的聽覺體驗。

#### **引用的著作**

1. Braille music \- RNIB, 檢索日期：12月 4, 2025， [https://www.rnib.org.uk/living-with-sight-loss/education-and-learning/braille-tactile-codes/braille-music/](https://www.rnib.org.uk/living-with-sight-loss/education-and-learning/braille-tactile-codes/braille-music/)  
2. A brief introduction to software tools used for accessible format conversion, 檢索日期：12月 4, 2025， [https://soundwithoutsight.org/hub-articles/a-brief-introduction-to-software-tools-used-for-accessible-format-conversion/](https://soundwithoutsight.org/hub-articles/a-brief-introduction-to-software-tools-used-for-accessible-format-conversion/)  
3. Percussion notation \- Wikipedia, 檢索日期：12月 4, 2025， [https://en.wikipedia.org/wiki/Percussion\_notation](https://en.wikipedia.org/wiki/Percussion_notation)  
4. How to Read Drum Notation: A Beginner's Guide \- Chagrin Valley Music, 檢索日期：12月 4, 2025， [https://chagrinvalleymusic.com/how-to-read-drum-notation/](https://chagrinvalleymusic.com/how-to-read-drum-notation/)  
5. How to Read Drum Sheet Music: A Beginner's Guide to Drum Notation \- UpBeat Studio, 檢索日期：12月 4, 2025， [https://upbeat.studio/how-to-read-drum-sheet-music-like-a-pro/](https://upbeat.studio/how-to-read-drum-sheet-music-like-a-pro/)  
6. Drum Notation & Sheet Music: How to Read It, 檢索日期：12月 4, 2025， [https://drumbeatsonline.com/blog/drum-notation-sheet-music-how-to-read-it](https://drumbeatsonline.com/blog/drum-notation-sheet-music-how-to-read-it)  
7. I wrote Drumming In All Directions to tackle a common problem- getting our limbs working together so we can play whatever comes to mind. Using 25 basic limb motions, DID provides a multi-limb workout that will test stamina, build coordination, speed and control for any drummer, any playing style\! \- Reddit, 檢索日期：12月 4, 2025， [https://www.reddit.com/r/Drumming/comments/junlfj/i\_wrote\_drumming\_in\_all\_directions\_to\_tackle\_a/](https://www.reddit.com/r/Drumming/comments/junlfj/i_wrote_drumming_in_all_directions_to_tackle_a/)  
8. iCons and Earcons: Critical but often overlooked tech skills \- Perkins School For The Blind, 檢索日期：12月 4, 2025， [https://www.perkins.org/resource/icons-and-earcons-critical-often-overlooked-tech-skills/](https://www.perkins.org/resource/icons-and-earcons-critical-often-overlooked-tech-skills/)  
9. Understanding Image Deskewing: A Mathematical Deep Dive with Python | by Sıla Kazan, 檢索日期：12月 4, 2025， [https://sila-kazan0626.medium.com/understanding-image-deskewing-a-mathematical-deep-dive-with-python-2f0d144acf64](https://sila-kazan0626.medium.com/understanding-image-deskewing-a-mathematical-deep-dive-with-python-2f0d144acf64)  
10. TrOMR:Transformer-based Polyphonic Optical Music Recognition \- GitHub, 檢索日期：12月 4, 2025， [https://github.com/NetEase/Polyphonic-TrOMR](https://github.com/NetEase/Polyphonic-TrOMR)  
11. liebharc/homr: homr is an Optical Music Recognition (OMR) software designed to transform camera pictures of sheet music into machine-readable MusicXML format. \- GitHub, 檢索日期：12月 4, 2025， [https://github.com/liebharc/homr](https://github.com/liebharc/homr)  
12. A detector for page-level handwritten music object recognition based on deep learning, 檢索日期：12月 4, 2025， [https://www.researchgate.net/publication/367305237\_A\_detector\_for\_page-level\_handwritten\_music\_object\_recognition\_based\_on\_deep\_learning](https://www.researchgate.net/publication/367305237_A_detector_for_page-level_handwritten_music_object_recognition_based_on_deep_learning)  
13. Toward a More Complete OMR Solution \- arXiv, 檢索日期：12月 4, 2025， [https://arxiv.org/html/2409.00316v1](https://arxiv.org/html/2409.00316v1)  
14. Comparative Analysis of Object Detection Models for Sheet Music Recognition: A Focus on YOLO and OMR Technologies \- ResearchGate, 檢索日期：12月 4, 2025， [https://www.researchgate.net/publication/385904852\_Comparative\_Analysis\_of\_Object\_Detection\_Models\_for\_Sheet\_Music\_Recognition\_A\_Focus\_on\_YOLO\_and\_OMR\_Technologies](https://www.researchgate.net/publication/385904852_Comparative_Analysis_of_Object_Detection_Models_for_Sheet_Music_Recognition_A_Focus_on_YOLO_and_OMR_Technologies)  
15. Efficient notation assembly in optical music recognition \- e-Repositori UPF, 檢索日期：12月 4, 2025， [https://repositori.upf.edu/items/b736edf9-0aed-413b-84f4-f89a14d13b49](https://repositori.upf.edu/items/b736edf9-0aed-413b-84f4-f89a14d13b49)  
16. OMR-Research/mung: Music Notation Graph \- GitHub, 檢索日期：12月 4, 2025， [https://github.com/OMR-Research/mung](https://github.com/OMR-Research/mung)  
17. Optical Music Recognition Datasets | OMR-Datasets \- GitHub Pages, 檢索日期：12月 4, 2025， [https://apacha.github.io/OMR-Datasets/](https://apacha.github.io/OMR-Datasets/)  
18. The DeepScoresV2 Dataset and Benchmark for Music Object Detection \- Semantic Scholar, 檢索日期：12月 4, 2025， [https://www.semanticscholar.org/paper/The-DeepScoresV2-Dataset-and-Benchmark-for-Music-Tuggener-Satyawan/912b1cfba9fc06da868f2b1ccfb0d36041449544](https://www.semanticscholar.org/paper/The-DeepScoresV2-Dataset-and-Benchmark-for-Music-Tuggener-Satyawan/912b1cfba9fc06da868f2b1ccfb0d36041449544)  
19. ka80/drumutation: Create LilyPond sheet music for all drum permutations \- GitHub, 檢索日期：12月 4, 2025， [https://github.com/ka80/drumutation](https://github.com/ka80/drumutation)  
20. CPJKU/msmd: A Multimodal Audio Sheet Music Dataset \- GitHub, 檢索日期：12月 4, 2025， [https://github.com/CPJKU/msmd](https://github.com/CPJKU/msmd)  
21. Improved Input | Audiveris Pages, 檢索日期：12月 4, 2025， [https://audiveris.github.io/audiveris/\_pages/guides/advanced/improved\_input/](https://audiveris.github.io/audiveris/_pages/guides/advanced/improved_input/)  
22. Percussion | MusicXML 4.0, 檢索日期：12月 4, 2025， [https://www.w3.org/2021/06/musicxml40/tutorial/percussion/](https://www.w3.org/2021/06/musicxml40/tutorial/percussion/)  
23. Element: unpitched \[group full-note\], 檢索日期：12月 4, 2025， [https://usermanuals.musicxml.com/MusicXML/Content/EL-MusicXML-unpitched.htm](https://usermanuals.musicxml.com/MusicXML/Content/EL-MusicXML-unpitched.htm)  
24. The application of Lempel-Ziv complexity in medicine science, nature science, social science, and engineering \- IEEE Xplore, 檢索日期：12月 4, 2025， [https://ieeexplore.ieee.org/iel8/6287639/6514899/10769414.pdf](https://ieeexplore.ieee.org/iel8/6287639/6514899/10769414.pdf)  
25. (PDF) Mathematical measures of syncopation \- ResearchGate, 檢索日期：12月 4, 2025， [https://www.researchgate.net/publication/228850033\_Mathematical\_measures\_of\_syncopation](https://www.researchgate.net/publication/228850033_Mathematical_measures_of_syncopation)  
26. Rhythmic pattern modeling for Beat and Downbeat Tracking in musical audio \- ISMIR, 檢索日期：12月 4, 2025， [https://archives.ismir.net/ismir2013/paper/000051.pdf](https://archives.ismir.net/ismir2013/paper/000051.pdf)  
27. If you can say it, you can play it \- Elephant Drums, 檢索日期：12月 4, 2025， [https://www.elephantdrums.co.uk/blog/creative-concepts/if-you-can-say-it-you-can-play-it/](https://www.elephantdrums.co.uk/blog/creative-concepts/if-you-can-say-it-you-can-play-it/)  
28. Using the Web Speech API \- MDN Web Docs, 檢索日期：12月 4, 2025， [https://developer.mozilla.org/en-US/docs/Web/API/Web\_Speech\_API/Using\_the\_Web\_Speech\_API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API/Using_the_Web_Speech_API)  
29. JavaScript Text-to-Speech \- The Easy Way \- AssemblyAI, 檢索日期：12月 4, 2025， [https://www.assemblyai.com/blog/javascript-text-to-speech-easy-way](https://www.assemblyai.com/blog/javascript-text-to-speech-easy-way)  
30. SpeechSynthesisUtterance: rate property \- Web APIs \- MDN Web Docs, 檢索日期：12月 4, 2025， [https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance/rate](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance/rate)  
31. Web Audio API \- MDN Web Docs \- Mozilla, 檢索日期：12月 4, 2025， [https://developer.mozilla.org/en-US/docs/Web/API/Web\_Audio\_API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)  
32. Synchronisation for Distributed Audio Rendering over Heterogeneous Devices, in HTML5, 檢索日期：12月 4, 2025， [https://repository.gatech.edu/server/api/core/bitstreams/d5a4d069-fca4-4cd1-995b-b7271828f04a/content](https://repository.gatech.edu/server/api/core/bitstreams/d5a4d069-fca4-4cd1-995b-b7271828f04a/content)  
33. Performance · Tonejs/Tone.js Wiki \- GitHub, 檢索日期：12月 4, 2025， [https://github.com/Tonejs/Tone.js/wiki/Performance](https://github.com/Tonejs/Tone.js/wiki/Performance)  
34. AudioContext: getOutputTimestamp() method \- Web APIs | MDN, 檢索日期：12月 4, 2025， [https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/getOutputTimestamp](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/getOutputTimestamp)  
35. Accessibility in React \- Learn web development | MDN, 檢索日期：12月 4, 2025， [https://developer.mozilla.org/en-US/docs/Learn\_web\_development/Core/Frameworks\_libraries/React\_accessibility](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Frameworks_libraries/React_accessibility)  
36. React accessibility: making your React app accessible \- TinyMCE, 檢索日期：12月 4, 2025， [https://www.tiny.cloud/blog/react-accessibility/](https://www.tiny.cloud/blog/react-accessibility/)  
37. Class Sampler \- Tone.js, 檢索日期：12月 4, 2025， [https://tonejs.github.io/docs/15.1.22/classes/Sampler.html](https://tonejs.github.io/docs/15.1.22/classes/Sampler.html)  
38. Tone.js, 檢索日期：12月 4, 2025， [https://tonejs.github.io/](https://tonejs.github.io/)  
39. Slider Pattern | APG | WAI \- W3C, 檢索日期：12月 4, 2025， [https://www.w3.org/WAI/ARIA/apg/patterns/slider/](https://www.w3.org/WAI/ARIA/apg/patterns/slider/)  
40. Media Seek Slider Example | APG | WAI \- W3C, 檢索日期：12月 4, 2025， [https://www.w3.org/WAI/ARIA/apg/patterns/slider/examples/slider-seek/](https://www.w3.org/WAI/ARIA/apg/patterns/slider/examples/slider-seek/)  
41. WCAG Compliance | Guide | AudioEye®, 檢索日期：12月 4, 2025， [https://www.audioeye.com/compliance/wcag/](https://www.audioeye.com/compliance/wcag/)  
42. Chapter 6: AUDITORY ICONS \- Bill Buxton, 檢索日期：12月 4, 2025， [https://www.billbuxton.com/AudioUI06icons.pdf](https://www.billbuxton.com/AudioUI06icons.pdf)  
43. Best Assistive Products for the Blind Musicians in 2025, 檢索日期：12月 4, 2025， [https://braillemusicandmore.com/best-assistive-products-for-the-blind-musicians-in-2025/](https://braillemusicandmore.com/best-assistive-products-for-the-blind-musicians-in-2025/)  
44. Navigation for the Blind through Audio-Based Virtual Environments \- PMC \- NIH, 檢索日期：12月 4, 2025， [https://pmc.ncbi.nlm.nih.gov/articles/PMC4259016/](https://pmc.ncbi.nlm.nih.gov/articles/PMC4259016/)  
45. Tips for teaching music to vision impaired students \- Macular Society, 檢索日期：12月 4, 2025， [https://www.macularsociety.org/professionals/teaching-resources/teaching-music/](https://www.macularsociety.org/professionals/teaching-resources/teaching-music/)  
46. Other Tools and Resources for Music Accessibility \- DSI | University of North Texas, 檢索日期：12月 4, 2025， [https://digitalstrategy.unt.edu/clear/teaching-resources/accessibility/music-accessibility/other-tools-and-resources-music-accessibility.html](https://digitalstrategy.unt.edu/clear/teaching-resources/accessibility/music-accessibility/other-tools-and-resources-music-accessibility.html)  
47. DEEP UNSUPERVISED DRUM TRANSCRIPTION \- ISMIR, 檢索日期：12月 4, 2025， [https://archives.ismir.net/ismir2019/paper/000020.pdf](https://archives.ismir.net/ismir2019/paper/000020.pdf)  
48. (PDF) Deep Learning Approaches for Automatic Drum Transcription \- ResearchGate, 檢索日期：12月 4, 2025， [https://www.researchgate.net/publication/377445557\_Deep\_Learning\_Approaches\_for\_Automatic\_Drum\_Transcription](https://www.researchgate.net/publication/377445557_Deep_Learning_Approaches_for_Automatic_Drum_Transcription)