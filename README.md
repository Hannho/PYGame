# PYGame
陳品睿的遊戲
!!!!!!　
圖片路徑要自己改喔
!!!!!!
一、初始化階段 (遊戲啟動)
建立角色池（setup_characters）

角色們有自己的基礎數值：HP、ATK、DEF、SPD、圖片。

計算速度排序

依照 speed 倒序排好攻擊順序，存在 turn_order 中。

載入背景圖片並設定視窗大小。

生成 UI 介面

攻擊者、目標的選單。

角色圖片、血條、基本資訊。

狀態總覽版（Status Board）。

戰鬥紀錄欄（Log）。

✅ 到這裡，玩家看到完整介面，遊戲待命中。

二、回合開始 (每次攻擊)
輪到某角色行動（根據速度順序 turn_order）

系統自動設定好「攻擊者」。

玩家選擇目標（選一個防守角色）

attacker_var 自動是當前輪到的角色。

defender_var 要玩家自己選，選一個其他角色。

按下「攻擊」按鈕（attack() 觸發）

系統檢查（在 attack() 函數中）

【攻擊者是否是正確的人？】✅

【攻擊者、目標都還活著？】✅

【攻擊者和目標不能是同一人？】✅

❗若有錯誤彈出 messagebox 提醒，停止流程。

三、執行攻擊 (傷害計算)
計算傷害公式：

damage = max(0, attacker.atk - defender.defense)
➔ 這裡是很經典的 RPG 算法：「攻擊力減掉防禦力，最低不小於0」。

扣除防守者 HP：

defender.take_damage(damage)
➔ HP 如果小於0，自動歸0。

更新 UI 顯示：

更新角色圖片、血條動畫（animate_health_bar）。

更新角色屬性文字。

更新 Status Board 狀態總覽。

紀錄攻擊結果到戰鬥記錄欄（log）

例：「海盜 攻擊 法師，造成 20 傷害。」

四、回合結束檢查
判斷遊戲是否結束：

if all(not c.is_alive() or c == attacker for c in self.characters)

只有攻擊者還活著 ➔ 宣告勝利

「🏆 XXX 是最後的勝利者！」

如果還沒結束 ➔ 輪到下一個活著的角色（next_turn()）

current_turn_index + 1，繼續下一位

自動設定新的 attacker_var

✅ 新回合開始！
