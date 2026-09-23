# 基準芯出しExcel レビュー・検討資料

作成日: 2026-09-24 01:50 JST
作成者: Codex (GPT-6)

**結論：現行結果を比較できる基準と共通数式の保守を整え、検索キー1セルへの集約は条件が揃う場合だけ採用します。全面的な事前計算表・係数化・カスタムマスター移行は今回見送ります。**

この一式には、QRから復元した参照用Excel、具体的な変更提案、回帰試験仕様、再検証ツールが含まれます。Excelの数式変更は0件です。本番帳票の代わりに配布・取込みするための候補ではありません。

## 最初に読む資料

| ファイル | 内容 |
|---|---|
| [レビュー・修正内容](docs/レビュー・修正内容.md) | 今回直した問題、検証結果、残る確認事項 |
| [Excel変更の実装計画書](docs/実装計画書.md) | 推奨範囲、採用条件、実装工程、切戻し、工数 |
| [数式変更一覧](docs/数式変更一覧.md) | 対象8セルの変更前式と変更後テンプレート |
| [回帰試験仕様](docs/回帰試験仕様.md) | 21セルとiPhone操作・保存・出力の比較項目 |
| [復元Excel](workbook/KSD-R1_restored.xlsx) | 調査した元の数式を確認する参照ブック |

変更セル仕様JSONの `{{SPEC_KEY_REFERENCE}}` は未確定の置換記号です。そのままExcelに貼り付けないでください。本番コピー・実セル番地・クラスターindexは実装開始時に確認します。

## Excelの収録範囲

復元ブックは14シート・936数式です。QRに入っていなかったExcelOutputSetting、出力③_DBの501行目以降、書式のみの空白セル・未収録の図や設定等は含まれません。これらを本番不具合として扱わず、推測で補っていません。本番の変更には完全な本番定義から出力したExcelが必要です。

ExcelのSHA-256：

```text
6afb0ea4fe142210f3f62e29f1718fa9408c95eb9d99e9a61a05b56ec4d50e20
```

## ZIPを受け取った場合

1. ZIPをフォルダーごと展開します。
2. `KSD-R1/README.md` と `docs/レビュー・修正内容.md` を読みます。
3. Excelは `workbook/KSD-R1_restored.xlsx` を開きます。

Python 3.10以降があれば、KSD-R1フォルダーで次の1コマンドにより整合性を再確認できます。追加ライブラリは不要です。Excelへの書込み・起動は行いません。

```powershell
python -X utf8 tools/check_package.py
```

PASSは、配布ファイルのハッシュ、Excelの936式、変更対象8式、置換の可逆性、依存先21セル、資料リンクの確認を意味します。iPhoneでの動作確認を意味しません。

## bundleテキストだけを受け取った場合

通常のテキストbundleはOfficeバイナリを直接収録しません。この一式では `payload/WorkbookPayload.json` に元Excelの全バイトを格納しています。

まずReversible-Script-Bundlerの `bundle_system.ps1` でテキストを展開します。以下のbundleファイル名と復元先は手元の場所に合わせて指定します。

```powershell
pwsh -NoProfile -File C:\Work_Codex\Reversible-Script-Bundler\bundle_system.ps1 -Mode Restore -RestoreInputPath .\bundle_260924_KSD-R1.txt -RestoreOutputPath .\restored
powershell -NoProfile -File .\restored\KSD-R1\tools\Restore-Workbook.ps1
python -X utf8 .\restored\KSD-R1\tools\check_package.py
```

Excelの復元処理はWindows PowerShell 5.1とPowerShell 7で実行できます。初回は `PASS_RESTORED`、既存Excelのハッシュが一致すれば `PASS_EXISTING` となります。不一致の既存Excelは上書きせず停止します。

bundle展開に必要な変換器自体はこの一式に同梱していません。変換器がない場合は、同時に用意したZIPを利用してください。

## 次の実装に必要なもの

- 本番Designerから出力した完全なExcelと帳票定義ID・revision。
- Designer、iPhoneアプリ、iOSの版と既存クラスター・出力設定。
- 現行の代表入力・期待出力と、Designer／iPhoneの検証環境。

これらを確認した後に、検索キー補助セルの採用を判断します。安全な配置や同等性を確認できなければ、現行式を保ったまま共通定義と照合だけを整備します。
