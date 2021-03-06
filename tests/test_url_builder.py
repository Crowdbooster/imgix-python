# -*- coding: utf-8 -*-

import imgix

from imgix.compat import urlparse


def default_builder():
    return imgix.UrlBuilder('my-social-network.imgix.net',
                            sign_with_library_version=False)


def default_builder_with_signature():
    return imgix.UrlBuilder('my-social-network.imgix.net', True, "FOO123bar",
                            sign_with_library_version=False)


def test_that_constants_are_exported():
    builder = imgix.UrlBuilder(
        'my-social-network.imgix.net',
        sign_mode=imgix.SIGNATURE_MODE_PATH,
        shard_strategy=imgix.SHARD_STRATEGY_CYCLE)
    assert builder._sign_mode == imgix.SIGNATURE_MODE_PATH
    assert builder._shard_strategy == imgix.SHARD_STRATEGY_CYCLE


def test_create():
    builder = imgix.UrlBuilder('my-social-network.imgix.net')
    assert type(builder) is imgix.UrlBuilder


def test_create_accepts_domains_list():
    domains = [
        'my-social-network-1.imgix.net',
        'my-social-network-2.imgix.net'
    ]
    builder = imgix.UrlBuilder(domains)
    assert builder._domains == domains


def test_create_accepts_domains_tuple():
    domains = (
        'my-social-network-1.imgix.net',
        'my-social-network-2.imgix.net'
    )
    builder = imgix.UrlBuilder(domains)
    assert builder._domains == domains


def test_create_accepts_domains_single_str():
    domains = 'my-social-network-1.imgix.net'
    builder = imgix.UrlBuilder(domains)
    assert builder._domains == [domains]


def test_create_url_with_path():
    builder = default_builder()
    url = builder.create_url("/users/1.png")
    assert url == "https://my-social-network.imgix.net/users/1.png"


def test_create_url_with_path_and_parameters():
    builder = default_builder()
    url = builder.create_url("/users/1.png", {"w": 400, "h": 300})
    assert url == "https://my-social-network.imgix.net/users/1.png?h=300&w=400"


def test_create_url_with_splatted_falsy_parameter():
    builder = default_builder()
    url = builder.create_url("/users/1.png", {"or": 0})
    assert url == "https://my-social-network.imgix.net/users/1.png?or=0"


def test_create_url_with_path_and_signature():
    builder = default_builder_with_signature()
    url = builder.create_url("/users/1.png")
    assert url == \
        "https://my-social-network.imgix.net/users/1.png" \
        "?s=6797c24146142d5b40bde3141fd3600c"


def test_create_url_with_path_and_paremeters_and_signature():
    builder = default_builder_with_signature()
    url = builder.create_url("/users/1.png", {"w": 400, "h": 300})
    assert url == \
        "https://my-social-network.imgix.net/users/1.png" \
        "?h=300&w=400&s=1a4e48641614d1109c6a7af51be23d18"


def test_create_url_with_fully_qualified_url():
    builder = default_builder_with_signature()
    url = builder.create_url("http://avatars.com/john-smith.png")
    assert url == \
        "https://my-social-network.imgix.net/"\
        "http%3A%2F%2Favatars.com%2Fjohn-smith.png" \
        "?s=493a52f008c91416351f8b33d4883135"


def test_create_url_with_fully_qualified_url_with_tilde():
    builder = default_builder()
    url = builder.create_url("http://avatars.com/john~smith.png")
    assert url == \
        "https://my-social-network.imgix.net/"\
        "http%3A%2F%2Favatars.com%2Fjohn~smith.png"


def test_create_url_with_fully_qualified_url_and_parameters():
    builder = default_builder_with_signature()
    url = builder.create_url("http://avatars.com/john-smith.png",
                             {"w": 400, "h": 300})
    assert url == \
        "https://my-social-network.imgix.net/" \
        "http%3A%2F%2Favatars.com%2Fjohn-smith.png" \
        "?h=300&w=400&s=a201fe1a3caef4944dcb40f6ce99e746"


def test_use_https():
    # Defaults to https
    builder = imgix.UrlBuilder('my-social-network.imgix.net')
    url = builder.create_url("/users/1.png")
    assert urlparse.urlparse(url).scheme == "https"

    builder = imgix.UrlBuilder('my-social-network.imgix.net', use_https=False)
    url = builder.create_url("/users/1.png")
    assert urlparse.urlparse(url).scheme == "http"

    builder = imgix.UrlBuilder('my-social-network.imgix.net', True)
    url = builder.create_url("/users/1.png")
    assert urlparse.urlparse(url).scheme == "https"

    builder = imgix.UrlBuilder('my-social-network.imgix.net', use_https=True)
    url = builder.create_url("/users/1.png")
    assert urlparse.urlparse(url).scheme == "https"


def test_utf_8_characters():
    builder = default_builder()
    url = builder.create_url(u'/ǝ')
    assert url == "https://my-social-network.imgix.net/%C7%9D"


def test_more_involved_utf_8_characters():
    builder = default_builder()
    url = builder.create_url(u'/üsers/1/米国でのパーティーします。.png')
    assert url == \
        "https://my-social-network.imgix.net/%C3%BCsers/1/" \
        "%E7%B1%B3%E5%9B%BD%E3%81%A7%E3%81%AE%E3%83%91%E3%83%BC%E3%83" \
        "%86%E3%82%A3%E3%83%BC%E3%81%97%E3%81%BE%E3%81%99%E3%80%82.png"


def test_param_values_are_escaped():
    builder = default_builder()
    url = builder.create_url('demo.png', {"hello world": "interesting"})

    assert url == "https://my-social-network.imgix.net/demo.png?" \
        "hello%20world=interesting"


def test_param_keys_are_escaped():
    builder = default_builder()
    url = builder.create_url('demo.png', {
        "hello_world": "/foo\"> <script>alert(\"hacked\")</script><"})

    assert url == "https://my-social-network.imgix.net/demo.png?" \
        "hello_world=%2Ffoo%22%3E%20%3Cscript%3Ealert%28%22" \
        "hacked%22%29%3C%2Fscript%3E%3C"


def test_base64_param_variants_are_base64_encoded():
    builder = default_builder()
    url = builder.create_url('~text', {
        "txt64": u"I cannøt belîév∑ it wors! 😱"})

    assert url == "https://my-social-network.imgix.net/~text?txt64=" \
        "SSBjYW5uw7h0IGJlbMOuw6l24oiRIGl0IHdvcu-jv3MhIPCfmLE"


def test_signing_url_with_ixlib():
    builder = imgix.UrlBuilder('my-social-network.imgix.net')
    url = builder.create_url("/users/1.png")
    assert url == (
        "https://my-social-network.imgix.net/users/1.png?ixlib=python-" +
        imgix._version.__version__)
