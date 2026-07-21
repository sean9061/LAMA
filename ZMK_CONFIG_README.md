# zmk-config-LAMA

roBaを改造したLAMAキーボード用のZMK config。[roBa本家のzmk-config](https://github.com/kumamuk-git/zmk-config-roBa)をベースに、実機の回路図(`pcb/v2/roBa_L`, `pcb/v2/roBa_R`)から読み取ったピン配置に合わせて作成。

## 本家からの変更点

- マイコンはXIAO nRF52840 **Plus**（回路図のシンボル`XIAO-nRF52840_Plus_SMD`から確認）。ただしZMKの`seeeduino_xiao_ble`ボード定義自体は無印/Plus共通のため、boardターゲットは変更していない。
- 左右とも小指側に1列ずつキーが増設されている（回路図上、左は`P1.07`、右は`P0.15`というPlus限定の拡張ピンを使った新しい列信号を確認）。
  - 行(row)・ロータリーエンコーダ・トラックボールSPI/IRQの配線は本家roBaと完全に同一。
  - 増設列に実際何個・どの行にキースイッチが実装されているかはPCBフットプリントで未確認のため、**全4行分を仮に確保**してある（未実装の位置は単に反応しないだけで害はない想定）。実際のキー数が判明したら`LAMA.dtsi`の`lama_physical_layout`と`default_transform`、`config/LAMA.keymap`の該当位置を調整すること。
- `config/LAMA.keymap`のcombos（tab, shift_tabなど）はキー位置番号が変わるため一旦削除。必要ならKeymapEditorで作り直す。
- `config/west.yml`は本家と同じZMK `v0.3-branch` + `kumamuk-git/zmk-pmw3610-driver`(main)に固定。PMW3610ドライバがこの組み合わせでのみ動作確認されているため、信頼性を優先した。

## ビルド

GitHub Actionsで自動ビルドされる（`.github/workflows/build.yml`）。生成される成果物:
- `LAMA_L-seeeduino_xiao_ble-zmk.uf2`
- `LAMA_R-seeeduino_xiao_ble-zmk.uf2`
- `settings_reset-seeeduino_xiao_ble-zmk.uf2`
