import io
import json
import base64
import requests
import oci
from fdk import response

def call_oic(oicbaseurl, oicusername, oicuserpwd, dbuserpwd):
    auth = (oicusername,oicuserpwd)
    headers = {
        "Content-Type": "application/json",
        "X-HTTP-Method-Override": "PATCH"
        }

    body = "{\"securityProperties\":[{\"propertyGroup\":\"CREDENTIALS\",\"propertyName\":\"Password\",\"propertyType\":\"PASSWORD\",\"propertyValue\":\"" + dbuserpwd + "\"}]}"

    try:
        r = requests.post(oicbaseurl,auth=auth, headers=headers, data=body)
    except (Exception) as error:
        print('ERROR: In calling OIC', error, flush=True)
        raise
    return 'STATUS: SUCCESS' if r.status_code == 200 else 'STATUS: ERROR - ' + str(r.status_code)

def get_secret(secret_ocid):
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    secrets_client = oci.secrets.SecretsClient(config={}, signer=signer)
    try:
        r = secrets_client.get_secret_bundle(secret_id=secret_ocid, stage="CURRENT")
    except (Exception) as error:
        print ('ERROR: In calling KMS', error, flush=True)
        raise

    return base64.b64decode(r.data.secret_bundle_content.content).decode("utf-8")


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

    oic_pwd = get_secret(oicuserpwdid)
    db_pwd = get_secret(dbuserpwdid)

    result = call_oic(oicbaseurl, oicusername, oic_pwd, db_pwd)

    return response.Response(
        ctx,
        response_data=json.dumps(result),
        headers={"Content-Type": "application/json"}
    )
