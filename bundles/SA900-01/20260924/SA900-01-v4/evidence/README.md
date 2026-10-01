# 検証証拠の読み方

作成日: 2026-09-24 02:09 JST<br>
作成者: Codex (GPT-6)

| ファイル | 内容 |
|---|---|
| `latest_summary.json` | v4候補SHA、試験計画SHA、実行IDと最終合否 |
| `static_validation.json` | 変更予定92セル、DB・レイアウト、依存関係の静的確認 |
| `native_finish.json` | Windows Excelでの保存・再オープンと基準入力の確認 |
| `native_acceptance.json` | 100回帰・15境界ケース、保護6項目のExcel実行記録 |
| `changes.json` | v3からv4へ内容を変えた全92セルの旧値・新値 |
| `review_probe_*.json`, `review_summary.json` | v3を読み取り専用で再計算した、実装前レビューの反例と集計 |
| `v3_latest_summary.json`, `v3_native_acceptance.json` | v3当時の検証記録。v4の合格記録ではない |

共有版では、元PCの絶対パスを`<source-workspace>`またはこのパッケージ内の相対パスへ置き換えました。試験の数値、ケースごとの合否、実行ID、候補・元ブックのSHA-256は保持しています。したがって、JSONファイル自体のSHA-256は元の記録と異なります。現在の完成品の判定には、v4の`latest_summary.json`と同じ候補SHAの証拠を用いてください。
