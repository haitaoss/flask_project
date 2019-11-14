from alipay import AliPay, ISVAliPay

app_private_key_string = open("/path/to/your/private/key.pem").read()
alipay_public_key_string = open("/path/to/alipay/public/key.pem").read()

alipay = AliPay(
    appid="",
    app_notify_url=None,  # 默认回调url
    app_private_key_string=app_private_key_string,
    # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
    alipay_public_key_string=alipay_public_key_string,
    sign_type="RSA"  # RSA 或者 RSA2
)