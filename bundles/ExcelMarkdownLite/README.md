# ExcelMarkdownLite 最新バンドル

作成日: 2026-09-01 05:36 JST
作成者: Codex (gpt-5.6-sol)
更新日: 2026-09-07

アプリ版1.1.1です。通常の文字列セルの書式取得を再利用し、数値セルの不要な補助処理も減らしました。ファイルを1つ選ぶ操作は同じです。画像やテキストボックスは省略してセルを変換し、部分的な文字装飾は警告付きでセル単位の書式へ近似します。旧バンドルは履歴として保持しています。

| 用途 | 最新ファイル | 収録数 |
|---|---|---:|
| 本体・保守・テスト一式 | [本体バンドル](bundle_260907_ExcelMarkdownLite_1_1_1.txt) | 98 |
| 初心者向け配布 | [初心者版バンドル](bundle_260907_ExcelMarkdownLite_Beginner_TextOnly_1_1_1.txt) | 38 |

対応する本体コミット: 1685cf3eeff35d922035daa520cc535091a6a199

## 復元と更新

Reversible-Script-BundlerのRestore機能で、新しいフォルダーへ復元してください。Windows版ExcelとWindows PowerShell 5.1が必要です。

初心者版では README.md を開いて初回手順を実行します。以前のショートカットを別名にしてから、新しいフォルダーの ExcelからMarkdownへを作る.bat でショートカットを作り直し、起動画面の1.1.1を確認してください。マクロ版は任意です。

本体版では tools/Restore-OfficeBinaryPayloads.ps1 をWindows PowerShell 5.1で実行すると、Officeファイル3件と空の.gitkeepをSHA-256検証付きで復元します。コミットした93ファイル一式が揃います。詳しくは BUNDLE_RESTORE.md を参照してください。

## 検証と速度

- 文字列・罫線・数式を含む5,000セル: 読み取り76.0秒から8.3秒、変換全体83.8秒から16.2秒。
- 数値中心100,000セル: 読み取り73.8秒から56.4秒、変換全体145.6秒から134.8秒。
- 同一入力と変換データの一致を確認。各状態1回、プレビューなしの測定です。結合セルや部分書式の多いブックなどでは効果が異なります。詳細は本体の PERFORMANCE_REPORT.md にあります。
- All品質ゲート: 47スクリプトPASS。通常版・初心者版のZIP展開、payload復元、起動、セル読み取りを含む回帰を確認しました。
- Gitに登録する実際のバンドルを復元し、本体98件・初心者版38件のSHA-256が一致しました。Office payload4件の復元と再実行PASS_EXISTING、本体正本93件のSHA一致、復元したソースの単体67/67件PASSを確認しました。
- 検証結果は BUNDLE_VERIFIED_GATE.json、正本の識別は BUNDLE_SOURCE_IDENTITY.json に収録しています。

実際の問題ブックと別PCのM365、32bit Excel、組織ポリシー、OneDrive実同期、物理的なファイル選択やCtrl+Cは未検証です。同じWindowsログイン内での複数変換の同時実行には対応していません。

## SHA-256

本体: ABAC9A9008EB7E1B6BCFB3A0D1CFC79CC0CE75A730195EDD875FABCBED905912

初心者版: 0E9879F2AC4831683AC7582BFADE94C676FA4BB0627ADACE60D9D18026FABAA8

Gitに登録するLF形式のバンドルのハッシュです。復元対象のファイル内容は変えていません。本体リポジトリにはremoteがなく、ローカルのコミット済みソース全体を共有バンドルに収録しています。