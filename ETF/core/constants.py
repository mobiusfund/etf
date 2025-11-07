RAWGIT_ROOT = 'https://raw.githubusercontent.com/mobiusfund/etf'
FIRST_BLOCK = 6706812
NETUID = 118
OWNER_UID = 0

COLDKEY_BL = 'https://api.app.trustedstake.ai/admin/blacklist'
INDEX_API = 'https://api.app.trustedstake.ai/admin/indexes'
INDEX_IDS = [
    '5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr',
    '5CiuGG5SYi4tkZRRHSBkDe85S38dEerofhBhohvFDsGCTYJh',
    '5E24XT6U2jvSNZe6gyZdgEGQkvNy59SY6ptDprMisrY8Dvsd',
    '5DmcwEMXrSxoGp6NKraDJHXxw4E6ZwmuMrpeggCvQqS5PLEe',
    '5DotNcrAQwCrmv6bEzyhEpgczHUsWyRc9yY4PCGM7u2G6yYE',
]
INDEX_LABEL = [
    'TSBCSI',
    'Top 10',
    'Full Stack',
    'Fintech',
    'Bittensor Universe',
]
INDEX_RATIO = [1 / len(INDEX_IDS)] * len(INDEX_IDS)

GAMMA = 1.00
KAPPA = 0.25
DNORM = 30
DMAX = 36500
