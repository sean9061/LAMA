# LAMA Project

自作キーボード（LAMA）のKiCadプロジェクト。左右分割、トラックボール付き。
[roBa](https://github.com/kumamuk-git/roBa)を改造したプロジェクトのため、フォルダ名や環境変数名（`ROBA_*`）には旧名称roBaが残っている。

## プロジェクト構成

- `pcb/v2/roBa_L/` — 左手側回路図・基板
- `pcb/v2/roBa_R/` — 右手側回路図・基板
- `pcb/KiCADv6/` — カスタムシンボル・フットプリント（TPS61221など）

## KiCad環境変数

`~/Library/Preferences/kicad/10.0/kicad_common.json` に設定：
- `ROBA_FP` — メインフットプリントライブラリ
- `ROBA_SYMBOL` — メインシンボルライブラリ
- `ROBA_V6_FP` — KiCADv6フォルダのフットプリント
- `ROBA_V6_SYM` — KiCADv6フォルダのシンボル

## 電源設計

- 電池（AA）→ `BAT_RAW` ネット → TPS61221DCKR（昇圧、3.3V固定出力）→ `Bat` ネット → XIAO nRF52840 Plus の **VBAT** ピン
- **注意**: VBATではなく **3V3ピンに接続するのが正しい設計**。VBATだとLDOのドロップアウトで動作不安定になる可能性がある。現在回路図上は `Bat` ネットがVBATに繋がっているが、ユーザーが手動で修正予定。
- TPS61221DCKR: EN=VIN（常時ON）、FB=VOUT（固定3.3V）

## ユーザーの方針

- **KiCadの回路図編集はユーザー自身が行う。Claudeにやらせない。**
- Claudeがファイルを直接編集するとトークンを大量消費して間違いが多い。
- 調査・確認・座標計算などの補助作業はClaudeに頼む。

## KiCadファイル操作の注意

- KiCadのy座標は回路図内で反転: `abs_y = center_y - lib_y`
- グリッド: 1.27mm (50 mil)
- lib_symbolのpin `(at x y angle)` のconnection pointは `(x, y)` そのもの（配置後は上記変換で絶対座標に変換）
