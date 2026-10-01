# 評価・変更記録テンプレートの使い方

作成日: 2026-10-02 00:10 JST
作成者: Codex (GPT-6)

`templates/`は未実施の記録ひな形です。実装時に別の作業フォルダーへ複製して記入します。空欄、null、NOT_RUNは未確認を表します。参照資料のハッシュや旧セル番地を、新しい本番の検証済み項目として転記しません。

## 1. ファイルと記入順序

| ファイル | 記入する情報 |
|---|---|
| [source_manifest.json](templates/source_manifest.json) | 最新完全版A/BのSHA、定義revision、マスター、設定、環境、ケース集合、元版への切戻し情報 |
| [bindings.json](templates/bindings.json) | 役割IDから現在のシート・セル・INDEXへの一意な対応。根拠、式全文、候補件数、型・設定を含む |
| [change_plan.json](templates/change_plan.json) | 候補名、書込み先、前提、許可範囲、変更前後の式・設定、候補SHA、実施状態 |
| [regression_cases.csv](templates/regression_cases.csv) | ケースの目的・層・入力/操作fixture・確認範囲・証拠参照。F01等はケース群のIDで、実ケースを必要数へ展開する |
| [functional_results.csv](templates/functional_results.csv) | 各case×engine×roleのA/B値と型・表示、結果、証拠 |
| [performance_measurements.csv](templates/performance_measurements.csv) | 1試行1行、A/Bの対番号、時間・環境・録画・欠測・除外理由 |
| [evaluation_summary.json](templates/evaluation_summary.json) | 必須gate、事前性能基準、件数、結果、採否、未実施と理由 |

JSONの`schema_version`はこの記録形式の版です。Excelやi-Reporterの版ではありません。対象が移動してもrole_idを保ち、`current`の対応とケースfixtureを更新します。意味が変わったものを同じrole_idのまま通しません。

## 2. 対応表の記入例

次は説明例で、実際のセルや設定の確定値ではありません。

```json
{
  "role_id": "OUT_MAIN_HALF_WIDTH",
  "status": "UNIQUE_VERIFIED",
  "candidate_count": 1,
  "current": {
    "sheet": "現在の出力シート名",
    "cell": "現在確認したセル",
    "cluster_index": "現行定義から確認したINDEX",
    "formula": "現在の式全文",
    "data_type": "現行定義から確認した型"
  },
  "evidence": [
    "VLOOKUPの返却列が元幅の列であり、取得後に/2を行う",
    "表示見出し、上流キー、下流判定、既存INDEXの対応が一致"
  ]
}
```

上記の文字列をそのまま実行情報へ貼りません。実施用記録では実際のセル、INDEX、式全文、ファイル参照に置き換えます。UNIQUE_VERIFIEDは候補が1個だっただけでは足りず、意味・設定・上流/下流まで照合できた状態です。

テンプレートには旧版の10出力役割、主キー・別キー、元表、元列の役割を載せています。キーの各要素、実入力、左右/符号/調整値の参照、依存出力、追加補助セル・行対応表の配置は、現行の棚卸しで追加します。初期テンプレートを全必要役割の一覧と見なさないでください。

## 3. 入力と期待値の型を保持する

各ケースのfixtureはJSONなどの別ファイルへ記録し、CSVから相対パスで参照します。操作順を配列で保存し、同じ値をA/Bへ投入します。直接代入で派生数式を壊さないでください。

```json
{
  "case_id": "F05_ZERO_001",
  "layer": "formula_unit",
  "initial_state_ref": "fixtures/initial_001.json",
  "operations": [
    {"order": 1, "role_id": "調査で確定した入力役割", "type": "number", "value": 0},
    {"order": 2, "role_id": "別の入力役割", "type": "string", "value": "0"}
  ]
}
```

これは数値0と文字列"0"を区別する形式例です。入力の役割は仮で、このまま使える実ケースではありません。`blank`は真の空欄、`string`と空の値は空文字、`error`はエラー種別も記録します。未丸め数値は取得エンジンの値を往復復元できる精度で保存し、丸めた表示値とは別にします。

`functional_results.csv`の`a_value_json`/`b_value_json`はJSONリテラルをCSVとして正しく引用します。値の型は別列です。型の取得不能、内部値の取得不能は結果を空欄でPASSにせず、NOT_RUNと理由を記録します。`evidence_ref`には画面・export・ログ等の実際のファイルを示します。

## 4. 性能記録の読み方

同じ`scenario_id,case_id,session_id,pair_id`の行にAとBを1行ずつ記録します。`order_in_pair`はAB/BA、`position_in_pair`は1/2です。`initial_state_ref`と`input_sequence_ref`は対内で同じものにします。

`elapsed_seconds`は実測値です。`result_status`は出力一致を確認した試行ならPASS、違えばFAIL、取得不能ならNOT_RUNとします。`measurement_status`はOK、EXCLUDED、MISSINGを使い、後二者は理由を記録します。除外しても行を削除しません。

録画ならt0/t1フレームと実fpsを記録します。ログならt0/t1時刻と時計の出典を記録します。計算から通信まで混ざった値を、計算時間だけとして書かないでください。端末・環境の詳細は`environment_ref`からsource_manifest等を参照できます。

集計時は対が揃い、出力一致し、測定条件が有効な試行だけを性能判定に用います。除外・失敗・欠測数も別に報告します。`performance_measurements.csv`は初期状態では見出しだけで、実測データはありません。

## 5. Gate記録と採否

evaluation_summaryの9個のgateは初期NOT_RUNです。PASSへ変更するときは実施コマンドや手順、日付、対象SHA/revision、件数、証拠ファイル、未確認範囲を記録します。資料のリンク検査やハッシュ照合だけでG04～G08をPASSへ変更しません。

推奨の性能基準は例ではなく、初回測定前に確定させる候補値です。変更する場合は測定前に理由を残します。採否は`NOT_EVALUATED`、`ADOPT`、`REJECT`、`INCONCLUSIVE`から選び、実装完了・実機合格・本番反映を別項目で管理します。

実装後の納品には、記入済みテンプレートと証拠を含めます。個人情報を含む実帳票は共有先の権限に合わせて保管し、評価に必要な値を消した資料を完全な証拠として扱いません。
