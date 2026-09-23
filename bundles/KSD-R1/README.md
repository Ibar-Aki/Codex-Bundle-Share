# KSD-R1 基準芯出しExcel・検討資料

作成日: 2026-09-24 02:00 JST
作成者: Codex (GPT-6)

最新版は **2026-09-24 レビュー・配布版** です。QR復元Excelと、iPhone i-Reporter用帳票の保守改善に関する検討資料をまとめています。

- [Excel・資料・復元ツール一式 ZIP](20260924/KSD-R1_review_20260924.zip)
- [テキストbundle（Excel復元payloadを含む）](20260924/bundle_260924_KSD-R1.txt)
- [読み始める資料](20260924/KSD-R1/README.md)
- [レビューと修正内容](20260924/KSD-R1/docs/レビュー・修正内容.md)
- [実装計画書](20260924/KSD-R1/docs/実装計画書.md)
- [参照用Excel](20260924/KSD-R1/workbook/KSD-R1_restored.xlsx)
- [配布物の最終検証記録](20260924/DELIVERY_VERIFICATION.json)

Excelの数式変更は0件です。本番定義の代わりに取り込む候補ではありません。既知のQR収録欠損はそのまま明記し、本番不具合として扱っていません。

今回の修正は、配布物へのExcel同梱、受取側で再実行できる検証、依存先の全件照合、適用済み判定の明確化、安全なExcel復元に限定しました。復元・破損・上書き防止の6テストと、Excel 16.0での全再計算を確認しています。Designer／iPhoneでの本番受入は未実施です。

bundleは22個のテキストファイルを収録し、標準の除外対象（.git、node_modules、生成物フォルダー等）を含めません。Excelバイナリはpayloadから同一バイトで復元できます。ZIPにはExcel本体とbundleの両方を含めています。

この共有リポジトリは2026-09-24確認時点で公開設定です。GitHubへプッシュすると、このExcelのデータ・数式および検討資料も閲覧可能になります。本番i-Reporterへの反映はGitHubへの保管とは別の操作です。
