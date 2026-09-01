# ExcelMarkdownLite 最新バンドル

作成日: 2026-09-01 05:36 JST

作成者: Codex (gpt-5.6-sol)

更新日: 2026-09-02

2026-09-02のワンクリック起動・初心者向けREADME修正版です。既存の古いバンドルは履歴として保持しています。

| 用途 | 最新ファイル | 収録数 |
|---|---|---:|
| 本体・保守・テスト一式 | [本体バンドル](bundle_260902_ExcelMarkdownLite.txt) | 88 |
| 初心者向け配布 | [初心者版バンドル](bundle_260902_ExcelMarkdownLite_Beginner_TextOnly.txt) | 35 |

対応する本体コミット: a1efca6b0d63ade9406e94dc3abf30f4cbfa2b3b

## 復元

Reversible-Script-BundlerのRestore機能で、選んだバンドルを新しいフォルダーへ復元してください。

本体版では、復元先の `tools/Restore-OfficeBinaryPayloads.ps1` をWindows PowerShell 5.1で実行します。元のOfficeファイル3件と空の `.gitkeep` をSHA-256検証付きで復元し、コミットされた83ファイル一式が揃います。詳しい手順は同梱の `BUNDLE_RESTORE.md` にあります。

初心者版では、最初に `README.md` を開いてください。`ExcelからMarkdownへを作る.bat` をダブルクリックすると、デスクトップに **ExcelからMarkdownへ** ショートカットを作成できます。マクロ版Excelは任意で、`マクロ版Excelを作る.bat` から復元できます。利用にはWindows版ExcelとWindows PowerShell 5.1が必要です。

## 確認結果

- fresh Release gate 8/8がPASS。通常版の配布受入18/18、初心者版はREADME確認を含む19/19がPASS。
- 本体bundleのテキスト88件を復元後、Office payload 4件を復元し、コミット済み83/83ファイルのSHA-256が一致。2回目のpayload復元は全件 `PASS_EXISTING`。
- 復元した本体でWindows PowerShell 5.1の単体67/67がPASS。
- 初心者版35/35ファイルのSHA-256が配布元と一致。`README.md` とワンクリックBATがあり、旧 `はじめに.md` はありません。
- 検出対象の秘密情報パターン、`.env`、credential系ファイル、Git内部、生成済みreleaseの混入は0件。
- gate証跡は本体bundleの `BUNDLE_VERIFIED_GATE.json`、正本83ファイルのhashは `BUNDLE_SOURCE_IDENTITY.json` に収録。

Core suite、別PC、別Excel版、組織ポリシー、実際のファイル選択画面、物理的なCtrl+C、OneDrive同期、100kセル性能再測定は今回の再検証に含めていません。

## SHA-256

本体: 48326E0EFDECCAB0B12BE7C0841759D0C78EE2425F6B0907AA0D009345062BEB

初心者版: 0458138F958C6BC3E62BD2CCBB680F7A57803E565CF3F51ABE5CE385FFB9A97F

上記は共有リポジトリのLF規約を適用したbundleのハッシュです。Base64内の復元対象ファイルのバイト列は変更していません。
