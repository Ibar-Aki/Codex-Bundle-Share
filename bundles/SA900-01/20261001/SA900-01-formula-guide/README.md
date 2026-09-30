# SA900-01 数式計算・軽量化 指示書

作成日: 2026-10-01 08:00 JST<br>
作成者: Codex (GPT-6)

このフォルダーは、SA900-01 v4の階名取得、階高・部品・取付位置へのつながり、VLOOKUP削減の意味を説明する指示書と、その比較根拠です。2026-09-30のチャット説明を整理し、2026-10-01に元Excelから数式数とSHA-256を再確認しています。

## 内容

| ファイル | 用途 |
|---|---|
| [指示書](SA900-01_数式計算と軽量化の指示書_20261001.md) | 計算の考え方、改善の量、互換性確認、保守時の注意 |
| [比較根拠](formula_comparison.json) | 比較対象3ファイルのSHA-256と数式集計 |
| [検証スクリプト](verify_formula_comparison.py) | 同じExcelから集計とSHA-256を再照合する読取専用ツール |
| [内容一覧](PACKAGE_MANIFEST.json) | 上記4ファイルのサイズとSHA-256 |

今回の配布物は文書と検証ツールです。Excelの数式変更は含みません。v4 Excel、修正書、解説書、復元用payloadは[既存の共有一式](../../20260924/SA900-01-v4/README.md)にあります。文書の単独復元時には、以下のGitHubリンクから既存の共有一式を参照してください。

- [v4共有一式](https://github.com/Ibar-Aki/Codex-Bundle-Share/tree/codex/sa900-01-v4-bundle-20260924/bundles/SA900-01/20260924)

## 検証の再実行

Python 3の標準ライブラリだけを使用します。復元マスター、v1、v4を含むフォルダーを指定してください。Excelの起動、再計算、保存は行いません。

```powershell
python verify_formula_comparison.py --workbook-directory "D:\path\to\workbooks"
```

3ファイルのSHA-256・数式集計が一致した場合だけ終了コード0と`PASS`を返します。対象不足、同名ファイルの重複、SHA不一致、集計不一致は`FAIL`です。v4だけでは3ファイル比較の検証は完了できません。比較元の復元マスターとv1は今回の文書bundleには含めていません。

## 復元

同じ保管階層の`bundle_261001_SA900-01-formula-guide.txt`から、このフォルダー内の5ファイルを復元できます。Reversible-Script-Bundlerの復元機能を使用してください。

```powershell
pwsh -File "C:\Work_Codex\Reversible-Script-Bundler\bundle_system.ps1" -Mode Restore -RestoreInputPath "D:\path\to\bundle_261001_SA900-01-formula-guide.txt" -RestoreOutputPath "D:\path\to\restored"
```

`DELIVERY_VERIFICATION.json`はbundleと同じ保管階層に置く配布検証記録です。bundle内には含めません。

## 確認済みと未確認

確認済み: 元Excelの同一性、保存された数式と結果の読取、比較集計、文書bundleの復元一致。

未確認: 1引数CONCATENATEのDesigner取り込み、欠落したExcelOutputSettingの復元、iPhone上の再計算、メーカー施工規定との照合、実機での処理時間。
