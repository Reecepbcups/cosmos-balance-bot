'''
Dict of chains in the following format:

{
    "ticker": [
        "LCD endpoints for proposals",
        {
            "ping": "https://ping.pub/ticker/gov/",
            "mintscan": "https://mintscan.io/ticker/proposals/",
        },
        "@twitter"
    ]
}

From: https://github.com/Reecepbcups/CosmosGovernanceProposalBot/blob/main/ChainApis.py
Will probably switch to ecostake cosmos directory in the future for here
'''

# /cosmos/bank/v1beta1/balances/<address>

chainAPIs = {
    "dig": [ 
        'https://api-1-dig.notional.ventures/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/dig/gov',
        },
        "@dig_chain"
        ],
    'juno': [
        'https://lcd-juno.itastakers.com/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/juno/gov',
            "mintscan": 'https://www.mintscan.io/juno/proposals',
        },
        "@JunoNetwork"
        ],
    'huahua': [
        'https://api.chihuahua.wtf/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/chihuahua/gov',
            "mintscan": 'https://www.mintscan.io/chihuahua/proposals',
        },
        "@ChihuahuaChain"
        ],
    'osmo': [
        'https://lcd-osmosis.blockapsis.com/cosmos/bank/v1beta1/balances/',
        {
            # "ping": 'https://ping.pub/osmosis/gov',
            "mintscan": 'https://www.mintscan.io/osmosis/proposals',
        },
        '@osmosiszone'
        ],
    'cosmos': [
        'https://lcd-cosmoshub.blockapsis.com/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/cosmos/gov',
            "mintscan": 'https://www.mintscan.io/cosmos/proposals',
        },
        "@cosmos"
        ],
    'akt': [
        'https://akash.api.ping.pub/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/akash-network/gov',
            "mintscan": 'https://www.mintscan.io/akash/proposals',
        },
        '@akashnet_'
        ],
    'stars': [
        "https://rest.stargaze-apis.com/cosmos/bank/v1beta1/balances/",
        {
            "ping": 'https://ping.pub/stargaze/gov',
        },        
        '@StargazeZone'
        ],
    'kava': [
        'https://api.data.kava.io/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/kava/gov',
            "mintscan": 'https://www.mintscan.io/kava/proposals',
        },        
        '@kava_platform'
        ],
    'like': [
        'https://mainnet-node.like.co/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/likecoin/gov',
        },        
        '@likecoin'
        ],
    'xprt': [
        'https://rest.core.persistence.one/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/persistence/gov',
            "mintscan": 'https://www.mintscan.io/persistence/proposals',
        },        
        '@PersistenceOne'
        ],
    'cmdx': [
        'https://rest.comdex.one/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/comdex/gov',
            "mintscan": 'https://www.mintscan.io/comdex/proposals',
        },        
        '@ComdexOfficial'
        ],
    "bcna": [ 
        'https://lcd.bitcanna.io/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/bitcanna/gov',
            "mintscan": 'https://www.mintscan.io/bitcanna/proposals',
        },        
        '@BitCannaGlobal'
        ],
    "btsg": [ 
        'https://lcd-bitsong.itastakers.com/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/bitsong/gov',
            "mintscan": 'https://www.mintscan.io/bitsong/proposals',
        },        
        '@BitSongOfficial'
        ],
    "band": [
        'https://laozi1.bandchain.org/api/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/band-protocol/gov',
            "mintscan": 'https://www.mintscan.io/akash/proposals',
        },        
        '@BandProtocol'
        ],
    "boot": [ # Bostrom
        'https://lcd.bostrom.cybernode.ai/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/bostrom/gov',
        },        
        ''
        ],
    "cheqd": [ 
        'https://api.cheqd.net/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/cheqd/gov',
        },        
        '@cheqd_io'
        ],
    "cro": [  
        'https://mainnet.crypto.org:1317/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/crypto-com-chain/gov',
            "mintscan": 'https://www.mintscan.io/crypto-org/proposals',
        },        
        '@cryptocom'
        ],
    "evmos": [  
        'https://rest.bd.evmos.org:1317/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/evmos/gov',
            "mintscan": 'https://www.mintscan.io/evmos/proposals',
        },        
        '@EvmosOrg'
        ],
    "fetch": [
        'https://rest-fetchhub.fetch.ai/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/fetchhub/gov',
            "mintscan": 'https://www.mintscan.io/fetchai/proposals',
        },        
        '@Fetch_ai'
        ],
    "grav": [  
        'https://gravitychain.io:1317/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/gravity-bridge/gov',
            "mintscan": 'https://www.mintscan.io/gravity-bridge/proposals',
        },        
        '@gravity_bridge'
        ],
    "inj": [  
        'https://public.lcd.injective.network/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/injective/gov',
            "mintscan": 'https://www.mintscan.io/injective/proposals',
        },        
        '@InjectiveLabs'
        ],
    "iris": [  
        'https://lcd-iris.keplr.app/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/iris-network/gov',
            "mintscan": 'https://www.mintscan.io/iris/proposals',
        },        
        '@irisnetwork'
        ],
    'iov': [ #Starname
        "https://lcd-iov.keplr.app/cosmos/bank/v1beta1/balances/",
        {
            "ping": 'https://ping.pub/starname/gov',
            "mintscan": 'https://www.mintscan.io/starname/proposals',
        },        
        '@starname_me'
        ],
    "lum": [  
        'https://node0.mainnet.lum.network/rest/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/lum-network/gov',
            "mintscan": 'https://www.mintscan.io/lum/proposals',
        },        
        '@lum_network'
        ],
    "regen": [  
        'https://regen.stakesystems.io/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/regen/gov',
            "mintscan": 'https://www.mintscan.io/regen/proposals',
        },        
        '@regen_network'
        ],
    "hash": [  
        'https://api.provenance.io/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/provenance/gov',
        },        
        '@provenancefdn'
        ],
    "secret": [  
        'https://api.scrt.network/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/secret/gov',
            "mintscan": 'https://www.mintscan.io/secret/proposals',
        },        
        '@SecretNetwork'
        ],
    "sent": [  
        'https://lcd-sentinel.keplr.app/cosmos/bank/v1beta1/balances/',        
        {
            "ping": 'https://ping.pub/sentinel/gov',
            "mintscan": 'https://www.mintscan.io/sentinel/proposals',
        },        
        '@Sentinel_co'
        ],
    "sif": [  
        'https://api.sifchain.finance:443/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/sifchain/gov',
            "mintscan": 'https://www.mintscan.io/sifchain/proposals',
        },        
        "@sifchain"
        ],
    "terra": [  
        'https://blockdaemon-terra-lcd.api.bdnodes.net:1317/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/terra-luna/gov',
        },        
        "@terra_money"
        ],
    "umee": [  
        'https://api.blue.main.network.umee.cc/cosmos/bank/v1beta1/balances/',
        {
            "ping": 'https://ping.pub/umee/gov',
            "mintscan": 'https://www.mintscan.io/umee/proposals',
        },        
        "@Umee_CrossChain"
        ],
    "craft": [ 
        'http://65.108.125.182:1317/cosmos/bank/v1beta1/balances/',
    ]
}