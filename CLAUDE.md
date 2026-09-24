# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# LAMA Project

自作キーボード（LAMA）のリポジトリ。左右分割、トラックボール付き、ロータリーエンコーダ搭載のBLEキーボード。
[roBa](https://github.com/kumamuk-git/roBa)を改造した派生プロジェクト（`upstream` remoteがroBa本家）。そのためフォルダ名・環境変数名・ファイル名（`roBa_L`, `ROBA_*`, `roba_L.kicad_sch`）には旧名称roBaが残っている。

リポジトリは**2つの独立した領域**からなる:

1. **ハードウェア** (`pcb/`, `case/`, `doc/`) — KiCadプロジェクトとケースSTL
2. **ファームウェア** (`config/`, `boards/`, `zephyr/`, `build.yaml`, `.github/workflows/`) — ZMK config（旧`zmk-config/`から直下へ展開済み。ZMKのuser-config構成をそのままリポジトリルートに置いている）

---

## ファームウェア（ZMK）

### ビルド

GitHub Actions（`.github/workflows/build.yml` → `zmkfirmware/zmk/.github/workflows/build-user-config.yml@v0.3-branch`）がpush時に自動ビルド。`build.yaml`のmatrixが成果物を決める:

- `LAMA_R-seeeduino_xiao_ble-zmk.uf2` — central側。`studio-rpc-usb-uart` snippet付き（ZMK Studio対応）
- `LAMA_L-seeeduino_xiao_ble-zmk.uf2` — peripheral側
- `settings_reset-seeeduino_xiao_ble-zmk.uf2`

ビルド済みuf2は `firmware/` に置かれている（未コミット）。

ローカルでビルドする場合はZMK標準の手順（`west init -l config` → `west update` → `west build -s zmk/app -b seeeduino_xiao_ble -- -DSHIELD=LAMA_R -DZMK_CONFIG=<repo>/config`）。

`config/west.yml`はZMK `v0.3-branch` + `kumamuk-git/zmk-pmw3610-driver`(main)に**意図的に固定**。PMW3610ドライバがこの組み合わせでのみ動作確認されているため。バージョンを上げる前にこの制約を確認すること。

LEDは `caksoylar/zmk-rgbled-widget`（`v0.3-branch`、ZMKのバージョンと必ず揃える）で、XIAO内蔵のRGB LEDにBluetoothの接続状態を表示している（`build.yaml` の `rgbled_adapter` shield）。layer_6の `&ind_con` で状態を再表示できる。

電池（`BAT_RAW`）はXIAOのどのピンにも繋がっておらず残量を測れないため、`CONFIG_ZMK_BATTERY_REPORTING=n` にしている。

`.github/workflows/draw.yml`（keymap-drawer、手動実行のみ）は `keymap_drawer.config.yaml` を参照するが、そのファイルはまだ存在しない。

### シールド構成 (`boards/shields/LAMA/`)

`LAMA.dtsi` が左右共通の定義（physical layout / matrix transform / kscan rows / encoder / sensors / trackballのプレースホルダ）を持ち、`LAMA_L.overlay` と `LAMA_R.overlay` がそれぞれ `col-gpios` と有効化するデバイスを上書きする、という構造。

- **マトリクス**: `default_transform` は 13列 × 4行、col2row。行GPIOは左右共通で `xiao_d 1/2/3/6`
- **列の割り当て**: L = 列0〜6（`col-offset`なし）、R = 列7〜12（`LAMA_R.overlay` で `col-offset = <7>`）。列番号はPCBのネット名 `Col0`〜に一致させてある
- **L側の列GPIO**（PCB確認済み）: Col0=`D10`（増設した小指列）, Col1=`P1.07`, Col2=`D9`, Col3=`D8`, Col4=`D7`, Col5=`P0.10`, Col6=`P0.09`（内側列）。本家roBaとは順番が違うので注意
- **R側の列GPIO**: Col0=`D10`, Col1=`D9`, Col2=`D8`, Col3=`D7`, Col4=`P0.10`, Col5=`P0.15`（増設した小指列）
- **キー数**: L 27（6/7/7/7、row1のCol6はエンコーダ押し込み）、R 24（6/7/7/4）。R側のrow3は内側キー（Col0,1）と親指（Col2,3）を兼ねる
- **L固有**: `left_encoder`（EC11、`xiao_d 5`/`xiao_d 0`）を有効化
- **R固有**: central役（`Kconfig.defconfig` の `ZMK_SPLIT_ROLE_CENTRAL`）。SPI0でPMW3610トラックボール（SCK=P0.05, MOSI/MISO=P0.04, CS=P0.09, IRQ=P0.02）、`xiao_serial` は無効化
- 行・エンコーダ・トラックボールSPI/IRQの配線は本家roBaと同一。列はL側で並び順が変わっている（上記）

### 未確定事項（作業時に注意）

- L側エンコーダの押し込みスイッチ（SW21）はPCB上でpad 1/2が未配線（D21のアノードもどこにも繋がっていない）。keymap上は位置を確保してあるが、押しても反応しない
- `config/LAMA.keymap` のcomboは増設でキー位置番号が変わるため削除済み。必要ならKeymapEditorで作り直す
- 増設列はデフォルトレイヤーで 左: Tab/Esc/Shift/⌃↑、右: BS/Enter/Shift/⌘Space。上位レイヤーは `&trans`
- 物理レイアウト（`LAMA.dtsi` / `config/LAMA.json`）はPCBのスイッチ座標から生成している

---

## ハードウェア（KiCad）

- `pcb/v2/roBa_L/` — 左手側回路図・基板（現行）
- `pcb/v2/roBa_R/` — 右手側回路図・基板（現行）
- `pcb/v1/` — 旧版
- `pcb/KiCADv6/` — カスタムシンボル・フットプリント（TPS61221など）
- `pcb/_kicad_symbols/`, `pcb/_kicad_footprints/` — メインライブラリ
- `pcb/pmw3610_breakout_for_roBa/`, `pcb/EVQWGD001_extension/` — サブ基板

### KiCad環境変数

`~/Library/Preferences/kicad/10.0/kicad_common.json` に設定（`fp-lib-table` / `sym-lib-table` から参照）:

- `ROBA_FP` — メインフットプリントライブラリ（`pcb/_kicad_footprints`）
- `ROBA_SYMBOL` — メインシンボルライブラリ（`pcb/_kicad_symbols`）
- `ROBA_V6_FP` — `pcb/KiCADv6/footprints.pretty`
- `ROBA_V6_SYM` — `pcb/KiCADv6`

**注意**: 現在これらは `/Users/seanfisher/Zatu_Projects/roBa/...` を指しているが、そのディレクトリは存在しない（リポジトリは `Zatu_Projects/LAMA/` にリネーム済み）。KiCadでライブラリが解決できない場合はこれが原因。

### 電源設計

電池（AA）→ `BAT_RAW` ネット → TPS61221DCKR（昇圧、3.3V固定出力、EN=VIN常時ON / FB=VOUT）→ XIAO nRF52840 Plus。

昇圧出力はVBATではなく**3V3ピンに接続するのが正しい設計**（VBATだとLDOのドロップアウトで動作不安定になる）。回路図上の出力ネットは L側が `3V3`、R側が `3.3V`（旧 `Bat` ネットは存在しない）ため修正済みと思われるが、配線の実体はKiCadで確認すること。

---

## ユーザーの方針

- **KiCadの回路図編集はユーザー自身が行う。Claudeにやらせない。** Claudeが直接編集するとトークンを大量消費して間違いが多い
- 調査・確認・座標計算などの補助作業はClaudeに頼む
- ファームウェア側（ZMK config）の編集はこの制約の対象外

## KiCadファイル操作の注意

- KiCadのy座標は回路図内で反転: `abs_y = center_y - lib_y`
- グリッド: 1.27mm (50 mil)
- lib_symbolのpin `(at x y angle)` のconnection pointは `(x, y)` そのもの（配置後は上記変換で絶対座標に変換）

## リポジトリ運用

- `.gitignore` が無いため、`.DS_Store` / KiCadの `.history/` / `export/` / `.kicad_prl` / `firmware/*.uf2` などが未追跡のまま大量に残っている。`git add -A` は避け、意図したファイルだけを個別にaddすること
- `case/trackballcase.stl` はGit LFS管理（`.gitattributes`）
- ルートの `fix_L_step2.py` は過去の回路図一括修正に使った使い捨てスクリプト。パスが旧 `Zatu_Projects/roBa` でハードコードされており、そのままでは動かない
- コミットメッセージは日本語
