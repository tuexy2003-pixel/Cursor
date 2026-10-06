import os,shutil,glob,sys
R='/workspace/creative-pipeline'; S=os.path.join(os.path.dirname(os.path.abspath(__file__)),'stage')
if os.path.exists(S): shutil.rmtree(S)
os.makedirs(S)
def cp(src,dst=None):
    src_abs=src if os.path.isabs(src) else os.path.join(R,src)
    dst=dst or src
    d=os.path.join(S,dst)
    if os.path.isdir(src_abs):
        shutil.copytree(src_abs,d,ignore=shutil.ignore_patterns('__pycache__','*.pyc'),dirs_exist_ok=True)
    else:
        os.makedirs(os.path.dirname(d),exist_ok=True); shutil.copy2(src_abs,d)
def cpg(pattern):
    hits=sorted(glob.glob(os.path.join(R,pattern)))
    if not hits: print('NO MATCH',pattern)
    for h in hits: cp(os.path.relpath(h,R))
for f in ['SYSTEM_PLAYBOOK.md','CATCHUP.md','HANDOFF_LATEST.md','logs/creative-tests.jsonl']: cp(f)
# proof_cand01_s2 (base + real cart screenshots without personal info + scripts)
P='outputs/proof_cand01_s2/'
for f in ['order_complete_v3.png','crop_price_summary.png','ref2_cfa_cart_items.png','crop_cart_top.png','dd_cart_mobile_01.png','dd_cart_mobile_02.png','_peek_cart.png','dd_cart_full_signedin.png','qa_slide2_v1.md','qa_slide2_v2.md']: cp(P+f)
cpg(P+'_w2/*.py'); cpg(P+'_work/*.py'); cp(P+'_work/quad.npy'); cp(P+'_work/green_filled.png')
# cand04 Wingstop
W='outputs/cand04_groceries_wingstop/'
for f in ['slide1_chat_916.png','slide2_order_916.png','_w/build_ws.py','_w/comp_ws.py','_w/rend.py','_w/chat_spec.json','_w/cover.png','_w/cover_sq.png','_w/w10.png','_w/w8.png','_w/order_complete_ws.png','_w/slide1_chat_full.png','_w/store.html','_w/old/build_ws_lemonade52.py','_w/ref/dd_header.png','_w/ref/dd_prices.png']: cp(W+f)
# cand04b Jalen part 2 (freezer slide = Tyrel attachment -> excluded)
J='outputs/cand04b_jalen_part2/'
for f in ['slide1_chat_916.png','freezer_prompt.txt','_w/chat_spec.json','_w/chat_spec_v2.json','_w/totals_crop.png','_w/slide1_chat_full.png']: cp(J+f)
cp(J+'freezer_prompt.txt','prompts/freezer_prompt.txt')
# cand05 Terrence
T='outputs/cand05_terrence_cheesecake/'
cpg(T+'*.png'); cpg(T+'_w/*.py'); cpg(T+'_w/*.json'); cpg(T+'_w/t_*.png'); cp(T+'_w/logo_cf.png'); cp(T+'_w/order_complete_cf.png'); cpg(T+'_w/slide1_chat_full*.png'); cp(T+'_w/src'); cp(T+'_w/ref')
# cand06 Isaiah
I='outputs/cand06_isaiah_chipotle/'
cpg(I+'*.png'); cpg(I+'_w/*.py'); cp(I+'_w/chat_spec.json'); cpg(I+'_w/t_*.png'); cp(I+'_w/logo_sq.jpg'); cp(I+'_w/order_complete_cp.png'); cp(I+'_w/slide1_chat_full.png'); cp(I+'_w/thumbs_view.png'); cp(I+'_w/z_rows.png'); cp(I+'_w/z_edges.png'); cp(I+'_w/ref')
# cand02 McDonald's (in_A/B/C + cash card source are Tyrel attachments -> excluded)
M='outputs/cand02_broke/'
for f in ['order_complete_mcd.png','composite_mcd_916.png','cash_card_8.09_916.png','cashcard_v2.py','_w/build_mcd.py','_w/comp_mcd.py','_w/rend.py','_w/visa_mark.png','_w/visa.png','_w/visa.svg','_w/mcd_arches.png','_w/quad_c.npy','_w/filled_c.png','_w/detect_c.py']: cp(M+f)
# cand01 Dre posted slides (ref.png = Tyrel attachment -> excluded)
D='outputs/cand01_final_916/'
for f in ['slide1_chat_916.png','slide1_chat_ios26_916.png','slide2_order_916.png','_w26/dre_spec.json','_w26/slide1_chat_ios26_full.png']: cp(D+f)
# shared tools + fonts
cp('outputs/_tools/build_imessage_ios26.py'); cp('outputs/_tools/build_imessage_ios26_pre_image.py.bak'); cp('outputs/_tools/ios26_assets')
cp('outputs/proof_cand01_s1/_w/fonts')
for f in glob.glob('/usr/share/fonts/truetype/sand-box/google/DM Sans/*.ttf'): cp(f,'fonts/DM Sans/'+os.path.basename(f))
# phone plates
A='assets/phone_plates/'
for f in ['user_A_iphone11_dark.jpg','user_B_bedsheet.jpg','user_C_car_thigh.jpg','user_D_hand_rings.jpg','quads.json','composite_on_plate.py','sr_cache.py','_models/FSRCNN_x2.pb']: cp(A+f)
cp(A+'_cache'); cp(A+'tests')
# skills
for s in ['source-card','adaptation-blitz-match','production-spec-qa','chat-story-slideshow']: cp('/home/box/agent-data/workflows/'+s,'skills/'+s)
# helper files written by this package
for f in ['requirements.txt','setup.sh','smoke_test.sh']:
    p=os.path.join(os.path.dirname(os.path.abspath(__file__)),f)
    if os.path.exists(p): shutil.copy2(p,os.path.join(S,f))
print('staged files:',sum(len(f) for _,_,f in os.walk(S)))
# raw DoorDash page dumps embed front-end API keys -> excluded (re-fetch with curl if needed)
rm=[]
for d,_,fs in os.walk(S):
    for f in fs:
        if f.endswith(('.html','.xml')): os.remove(os.path.join(d,f)); rm.append(os.path.relpath(os.path.join(d,f),S))
print('removed raw page dumps:',rm)
