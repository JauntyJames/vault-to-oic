import io
import json
import base64
import requests
import oci
from fdk import response

def call_oic(oicbaseurl, oicusername, oicuserpwd, dbuserpwd):
    auth = (oicusername,oicuserpwd)
    headers = {"Content-Type": "application/json"}

    body = "{\"securityProperties\":[{\"propertyName\":\"password\",\"propertyValue\":" + dbuserpwd + "}]}"

    try:
        r = requests.post(oicbaseurl,auth=auth, headers=headers, data=body)
    except (Exception) as error:
        print('ERROR: In calling OIC', error, flush=True)
        raise
    return 'STATUS: SUCCESS' if r.status_code == 200 else 'STATUS: ERROR - ' + str(r.status_code)

def get_secrets(oicuserpwdid, dbuserpwdid):
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    secrets_client = oci.secrets.SecretsClient(config={},
        signer=signer)
    try:
        r = oci.secrets.SecretsClient.get_secret_bundle(oicuserpwdid)
    except (Exception) as error:
        print ('ERROR: In calling KMS', error, flush=True)
        raise
    oic_pwd = r.secret_bundle_content

    try:
        r = oci.secrets.SecretsClient.get_secret_bundle(dbuserpwdid)
    except (Exception) as error:
        print ('ERROR: In calling KMS', error, flush=True)
        raise
    db_pwd = r.secret_bundle_content
    return oic_pwd, db_pwd


def handler(ctx, data: io.BytesIO=None):
    try:
        cfg = ctx.Config()
        oicbaseurl = cfg["oic_base_url"]
        oicusername = cfg["oic_username"]
        oicuserpwdid = cfg["oic_userpwd_id"]
        dbuserpwdid = cfg["db_userpwd_id"]

    except Exception:
        print('Missing function parameter(s)', flush=True)
        raise
    oic_pwd, db_pwd = get_secrets(oicuserpwdid, dbuserpwdid)

    result = call_oic(oicbaseurl, oicusername, oic_pwd, db_pwd)

    return response.Response(
        ctx,
        response_data=json.dumps(result),
        headers={"Content-Type": "application/json"}
    )
