[SSOT MANDATE]
- DUMMY/SIM/媛??湲덉?
- RUN 利앷굅 ?놁쑝硫?FAIL
- ???ㅻ뜑 ?놁쑝硫??ㅽ뻾 湲덉?




?꾨옒 SSOT_ORDER_ID ?묒뾽???섑뻾?? ?섏젙? 1~3?뚯씪濡??쒗븳, ?꾨즺 ???ㅽ뻾 而ㅻ㎤??蹂寃쏀뙆??紐⑸줉/run 利앷굅寃쎈줈瑜?諛섎뱶??異쒕젰??

[SSOT_ORDER_ID] G7X_ORDER_12_ORDER_BUNDLE_README_V1_20260117
[ROOT] C:\g7core\g7_v1
[MODE] CLAUDE_CODE
[FILES_LIMIT] 1-3

[STEP0_MODEL_LOCK_REQUIRED]
?묒뾽 ?쒖옉 吏곹썑 Claude Code??/model ?ㅽ뻾
?섏삩 寃곌낵瑜??꾨즺 蹂닿퀬 泥?以꾩뿉 諛섎뱶???ы븿
MODEL_STAMP: (?ш린??/model 異쒕젰 洹몃?濡?
?꾨씫 ??FAIL

[GOAL]
?ㅻ뒛 留뚮뱺 GPTORDER ?섏껌 ?ㅻ컻???대뼸寃??ㅽ뻾?섎뒗吏(異붿쿇 ?쒖꽌 01~06, 利앷굅 ?섏쭛) DOCS\SSOT_ORDER_BUNDLE_GUIDE_V1.md濡??뺣━?쒕떎.

[PATCH_SCOPE]
C:\g7core\g7_v1\DOCS\SSOT_ORDER_BUNDLE_GUIDE_V1.md

[RUN_COMMANDS]
cd C:\g7core\g7_v1
Get-Item .\DOCS\SSOT_ORDER_BUNDLE_GUIDE_V1.md

[DELIVERABLES]
MODEL_STAMP(泥?以?
蹂寃??뚯씪 紐⑸줉(寃쎈줈 ?ы븿)
?ㅽ뻾 而ㅻ㎤??蹂듬텤??
run 利앷굅寃쎈줈 1以?RUN_PATH=...)

[FAIL_FAST]
MODEL_STAMP ?꾨씫 = FAIL
1~3?뚯씪 ?쒗븳 ?꾨컲 = FAIL
ROOT 諛??섏젙 = FAIL
DELIVERABLES ?꾨씫 = FAIL


