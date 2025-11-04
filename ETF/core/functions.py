# Copyright © 2025 Mobius Fund

import os, math, requests
import bittensor as bt
import pandas as pd
from .constants import *

def update():
    init = 'ETF/__init__.py'
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    lv = open(f'{root}/{init}').read()
    rv = requests.get(f'{RAWGIT_ROOT}/refs/heads/main/{init}').text
    lv, rv = [eval(v.split('\n')[0].split('=')[1]) for v in [lv, rv]]
    ln, rn = [sum(int(n) * 100 ** i for i, n in enumerate(v.split('.')[::-1])) for v in [lv, rv]]
    if ln >= rn: return
    print(f'Updating... {lv} -> {rv}')
    cmd = f'cd {root}; git pull && pip install -e .'
    err = os.system(cmd)
    if err: print(f'Update failed. Please manually update using command:\n{cmd}')
    else: print('Update succeeded')
    return err

def score(netuid=NETUID):
    sc = pd.DataFrame(columns=['uid', 'hotkey', 'coldkey', 'count', 'index', 'block', 'balance', 'score'])
    ckblk = [{d['address']:d['fromBlock'] for d in requests.get(f'{INDEX_API}/{i}').json()['delegators']
        if d['type'] == 'Staking' and d['address'] not in requests.get(COLDKEY_BL).json()} for i in INDEX_IDS]
    ckbal = {}

    st = bt.Subtensor('finney')
    mg = st.get_metagraph_info(netuid)
    nn = st.all_subnets()

    def scoring(bal, blk):
        return bal ** GAMMA * (1 + KAPPA * math.log(1 + min((mg.block - blk) / 7200, DMAX) / DNORM)) if mg.block > blk else float('nan')

    def balance(ck):
        return sum([float(s.stake) * float(nn[s.netuid].price) for s in st.get_stake_for_coldkey(ck) if s.netuid])

    for ck in set(mg.coldkeys): ckbal[ck] = balance(ck)
    for i in range(len(mg.rank)):
        hk, ck = mg.hotkeys[i], mg.coldkeys[i]
        try:
            idx = [ck in kk for kk in ckblk].index(True)
            blk = max(ckblk[idx][ck], FIRST_BLOCK)
        except: idx, blk = [float('nan')] * 2
        bal = ckbal[ck]
        sc.loc[len(sc)] = i, hk, ck, 0, idx, blk, bal, scoring(bal, blk)

    sc['count'] = sc.join(sc.groupby('coldkey').count()['uid'], 'coldkey', lsuffix='_')['uid']
    sc['score'] /= sc['count']

    ir = INDEX_RATIO if len(INDEX_RATIO) == len(INDEX_IDS) else []
    scz = sc['score'].sum()
    for i in range(len(ir)):
        sci = sc[sc['index'] == i]['score'].sum()
        if sci: sc.loc[sc['index'] == i, 'score'] *= ir[i] * scz / sci

    tt = sc[~sc['index'].isna()]['balance'].sum()
    it = [sc[sc['index'] == i]['balance'].sum() for i in range(len(INDEX_IDS))]
    ic = [len(sc[sc['index'] == i]) for i in range(len(INDEX_IDS))]

    sc['balance'] = sc['balance'].round(2)
    sc.loc[sc['score'].isna(), 'score'] = 0
    if not sc['score'].sum(): sc.loc[sc['uid'] == OWNER_UID, 'score'] = 1

    ir = str([f'{i:.2f}' for i in ir]).replace("'", '')
    it = str([f'{i:.2f}' for i in it]).replace("'", '')
    print(sc.sort_values(['score', 'block'], na_position='first').to_string(index=False))
    print(f'index ratio: {ir}')
    print(f'index total: {it}, total: {tt:.2f} TAO')
    print(f'miner count: {ic}, total: {sum(ic)}')

    return sc['score'].values
