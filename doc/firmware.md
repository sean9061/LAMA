# LAMA のファームウェア（ZMK）

[roBa 本家の zmk-config](https://github.com/kumamuk-git/zmk-config-roBa) をもとに、LAMA の基板のピン配置に合わせて作り直したものです。ZMK の user config の構成を、そのままリポジトリの直下に置いています。

## ファイル

| ファイル | 内容 |
|---|---|
| `boards/shields/LAMA/LAMA.dtsi` | 左右で共通の定義（物理レイアウト、マトリクス、行の GPIO、エンコーダ、トラックボールの枠） |
| `boards/shields/LAMA/LAMA_L.overlay` / `LAMA_R.overlay` | 左右それぞれの列の GPIO と、有効にするデバイス |
| `boards/shields/LAMA/LAMA_L.conf` / `LAMA_R.conf` | 左右それぞれの Kconfig |
| `config/LAMA.keymap` | キーマップ |
| `config/LAMA.json` | 物理レイアウト（KeymapEditor・keymap-drawer 用） |
| `config/west.yml` | 使う ZMK とモジュールの版 |
| `build.yaml` | GitHub Actions でビルドする組み合わせ |

## 版の固定

`config/west.yml` は、ZMK を `v0.3-branch`、トラックボールのドライバ [kumamuk-git/zmk-pmw3610-driver](https://github.com/kumamuk-git/zmk-pmw3610-driver) を `main` に固定しています。PMW3610 のドライバが、この組み合わせでしか動作を確認できていないためです。ZMK の版を上げる前に、ドライバが対応しているかを確かめてください。

LED の表示に使う [zmk-rgbled-widget](https://github.com/caksoylar/zmk-rgbled-widget) も `v0.3-branch` です。ZMK と必ず同じ版にそろえます。

## 左右の役割

- **右手（`LAMA_R`）が central。** パソコンとつながるのは右手で、トラックボール（PMW3610）と ZMK Studio も右手にある。`build.yaml` で `studio-rpc-usb-uart` の snippet を付けている
- **左手（`LAMA_L`）は peripheral。** ロータリーエンコーダの設定は左手で有効にしている
- 左右とも `rgbled_adapter` の shield を付け、XIAO 内蔵の RGB LED に Bluetooth の接続状態を出す。SYSTEM レイヤーの「接続表示」（`&ind_con`）で、いまの状態をもう一度表示できる

## マトリクスとピン配置

13列 × 4行、ダイオードの向きは col2row です。列の番号は、基板のネット名 `Col0`〜 に合わせています。

| | GPIO |
|---|---|
| 行（左右共通） | `D1`, `D2`, `D3`, `D6` |
| 左手の列 Col0〜Col6 | `D10`（増設した小指の列）, `P1.07`, `D9`, `D8`, `D7`, `P0.10`, `P0.09`（内側の列） |
| 右手の列 Col0〜Col5 | `D10`, `D9`, `D8`, `D7`, `P0.10`, `P0.15`（増設した小指の列） |
| エンコーダ（左手） | A=`D5`, B=`D0` |
| トラックボール（右手、SPI0） | SCK=`P0.05`, MOSI/MISO=`P0.04`, CS=`P0.09`, IRQ=`P0.02` |

- 右手の列は、`LAMA_R.overlay` の `col-offset = <7>` で 7〜12 番として扱う
- 左手の列の並びは roBa 本家と違う。行・エンコーダ・トラックボールの配線は本家と同じ
- 増設した列には、XIAO nRF52840 **Plus** にしかないピン（左 `P1.07`、右 `P0.15`）を使っている。ボードの定義は無印と共通の `seeeduino_xiao_ble` のまま
- 右手の row3 は、内側のキー（Col0, 1）と親指のキー（Col2, 3）を兼ねている
- 物理レイアウト（`LAMA.dtsi` と `config/LAMA.json`）は、基板上のスイッチの座標から作っている
- スイッチの数は左手 26（row0・row1 が Col0〜5、row2・row3 が Col0〜6。row1 の Col6 はエンコーダの位置）、右手 24（全行 Col0〜5）。上の GPIO とあわせて `pcb/v2/` の基板と照合済み

## キーマップ

キー配置図は [keymap-drawer/LAMA.svg](../keymap-drawer/LAMA.svg) です。ブラウザで開くと押したキーが光る [keymap.html](keymap.html) もあります（`python3 doc/keymap_gen.py` で `config/LAMA.keymap` と `config/LAMA.json` から作り直す。ZMK Studio で変えた内容は反映されない）。

- **増設した列**は、BASE で 左: Esc / Tab / Shift / ⌃↑（Mission Control）、右: ⌫ / ⏎ / Shift / ⌘Space（Spotlight）。ほかのレイヤーでは下のレイヤーを透過する
- **右手 row3 の Col4** は右⌘（`RGUI`）。音声入力アプリ VoiceOS のトリガーにしている（VoiceOS は F13 以降のキーをトリガーにできない）
- **英数・かな**（`&lt_to_layer_0`）は、長押しでレイヤー（SYSTEM / ARROW）、タップで BASE に戻ってから英数・かなを送る
- **FUNCTION** の左手は、明るさ（W/E）、前の曲・再生/停止・次の曲（S/D/F）、ミュート・音量（X/C/V）、スクリーンショット（T: ⇧⌘4、G: ⇧⌘5）。NUM の数字はテンキーなので、Mac のスクリーンショットのショートカットには使えない
- **ARROW** の X/V はブラウザの戻る/進む（⌘[ / ⌘]）。エンコーダを回すとタブを切り替える（⌃PgUp / ⌃PgDn）
- エンコーダは BASE で PgUp / PgDn
- roBa 本家にあった combo は、キーの位置番号が変わったため外している。使いたいときは KeymapEditor などで作り直す

### トラックボール

- ボールを動かすと MOUSE レイヤー（4）に切り替わり、止めてから 700ms（`CONFIG_PMW3610_AUTOMOUSE_TIMEOUT_MS`）で戻る
- タイピングの振動で切り替わらないよう、1回の読み取りで縦横の移動量の合計が `CONFIG_PMW3610_MOVEMENT_THRESHOLD`（いまは 3）を超えたときだけ切り替える。誤爆するなら上げ、動かし始めが鈍いなら下げる（0 だと振動で切り替わり、5 だと鈍かった）
- SCROLL レイヤー（5）では、ボールでスクロールする
- 解像度などの設定は `LAMA_R.conf` にある

## 電池

電池（`BAT_RAW`）は XIAO のどのピンにもつながっておらず、残量を測れません。そのため `CONFIG_ZMK_BATTERY_REPORTING=n` にしています。

## ローカルでビルドする

GitHub Actions を使わずにビルドするときは、ZMK の標準の手順に従います。

```sh
west init -l config
west update
west build -s zmk/app -b seeeduino_xiao_ble -S studio-rpc-usb-uart -- -DSHIELD="LAMA_R rgbled_adapter" -DZMK_CONFIG="$PWD/config" -DZMK_EXTRA_MODULES="$PWD"
```

左手は `-S studio-rpc-usb-uart` を外し、`-DSHIELD="LAMA_L rgbled_adapter"` にします。

## わかっている問題

- 左手のエンコーダの押し込みスイッチ（SW21）は、基板上で配線されていない。キーマップ上は位置を確保してあるが、押しても反応しない
