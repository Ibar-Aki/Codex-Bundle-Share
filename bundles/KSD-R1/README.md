# KSD-R1 基準芯出しExcel・検討資料

作成日: 2026-09-24 02:00 JST
作成者: Codex (GPT-6)
更新日: 2026-10-02

最新の実装・評価指示書は **2026-10-02 統合版** です。入力・操作・計算結果・出力を変えずに軽くするという最新条件に従い、セル位置・軽微な版変更への対応と、改善前後のiPhone評価をまとめました。

- [統合資料の入口](20261002/KSD-R1-LLM-Guide/README.md)
- [LLM向け統合実装指示書](20261002/KSD-R1-LLM-Guide/LLM_IMPLEMENTATION_GUIDE.md)
- [改善前後の評価仕様](20261002/KSD-R1-LLM-Guide/EVALUATION_PROTOCOL.md)
- [LLMへの依頼文](20261002/KSD-R1-LLM-Guide/LLM_TASK_PROMPT.txt)
- [統合資料 ZIP](20261002/KSD-R1_LLM_Guide_20261002.zip)

統合版は文書と未記入の試験テンプレートです。候補Excelの変更・Designer取り込み・iPhone受入・本番反映は未実施です。実装時には最新の完全な本番Excelと帳票定義を比較基準にします。

以下の **2026-09-24 レビュー・配布版** は、QR復元Excelと当時の保守改善資料を保管する旧版です。以前の提案と新しい制約が矛盾する場合は、上の統合版を優先してください。

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
