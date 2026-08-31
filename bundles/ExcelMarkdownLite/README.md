# ExcelMarkdownLite 最新バンドル

作成日: 2026-09-01 05:36 JST

作成者: Codex (gpt-5.6-sol)

2026-09-01のレビュー修正版です。既存の古いバンドルは履歴として保持しています。

| 用途 | 最新ファイル | 収録数 |
|---|---|---:|
| 本体・保守・テスト一式 | [本体バンドル](bundle_260901_ExcelMarkdownLite.txt) | 87 |
| 初心者向け配布 | [初心者版バンドル](bundle_260901_ExcelMarkdownLite_Beginner_TextOnly.txt) | 34 |

対応する本体コミット: 9ace43eaf5e8ac16615bba276a67e875d9f34dbe

## 復元

Reversible-Script-BundlerのRestore機能で、選んだバンドルを新しいフォルダーへ復元してください。

本体版では、復元先のtools/Restore-OfficeBinaryPayloads.ps1をWindows PowerShell 5.1で実行します。元のOfficeファイル3件と空の.gitkeepをSHA-256検証付きで復元し、コミットされた82ファイル一式が揃います。詳しい手順は同梱のBUNDLE_RESTORE.mdにあります。

初心者版では、復元先の「マクロ版Excelを作る.bat」でランチャーExcelを復元できます。通常のExcel→Markdown変換はapp/Start-ExcelToMarkdown.ps1から起動できます。Windows版Excelが必要です。

## 確認結果

- コミット対象のGit blobから87/87・34/34ファイルを復元し、全ファイルのSHA-256が一致。
- 本体の元82ファイル、初心者版の復元XLSMも元データと一致。
- 復元後の単体67項目、基本往復6項目がPASS。
- 本体・初心者版それぞれで追加単体55項目、起動23項目、実Excel36項目がPASS。
- 復元XLSMを両方ともExcelで再オープンし、シート1枚・ボタン4個と終了処理を確認。
- 検出対象の秘密情報パターン0件。Git内部、配布ZIP、実行ログ、不要な試験生成物は収録対象外。
- 元のAllゲート25系列の検証記録は本体バンドルのBUNDLE_VERIFIED_GATE.jsonに収録。実装ファイルはその検証時点と一致します。

別PC、別Excel版、組織ポリシー、手動の画面操作、100kセル性能再測定は今回の公開検証に含めていません。

## SHA-256

本体: 92B8B8DB6C28DCA4FE05AA81CA53EFDE26EB93C8D3323024E6AC7E92BCAC8926

初心者版: ACD9C516F99E25320A1E4C06E231B9C177BA2E1632A186605B94A812B02F509E

上記は共有リポジトリのLF規約を適用した、実際のコミット対象バンドルのハッシュです。Base64内の復元対象ファイルのバイト列は変更していません。