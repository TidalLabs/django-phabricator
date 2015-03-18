import json
from mock import Mock, MagicMock

def prep_phab_mocks():
    phabricator = MagicMock()
    phabricator.user.query = MagicMock(return_value=get_dummy_users())
    phabricator.project.query = MagicMock(return_value=get_dummy_projects())
    phabricator.repository.query = MagicMock(return_value=get_dummy_repos())
    phabricator.differential.query = MagicMock(side_effect=get_batched_diffs)

    return phabricator


class ResponseWrapper(object):
    """
    Because python-phabricator's raw values (which we use) are available only through the
    ``response`` attribute, we need to wrap our dummy data similarly
    """
    def __init__(self, data, *args, **kwargs):
        self.response = data
        super(ResponseWrapper, self).__init__(*args, **kwargs)


def get_batched_diffs(order=None, limit=None, offset=0):
    diffs = get_dummy_diffs(order)

    # This is a PITA becase we have to slice a dict in a consistent manner
    if order:
        # convert diffs to list of tuples sorted by modification date descending
        ordered_map = sorted(diffs.items(), key=lambda tup: tup[1]['dateModified'], reverse=True)

        # and then retrieve just the keys
        ordered_keys = [item[0] for item in ordered_map]

    else:
        # Order doesn't matter except that we need it to be consistent across calls
        ordered_keys = sorted(diffs.keys())

    if limit:
        keys_to_retrieve = ordered_keys[offset:offset+limit]
    else:
        keys_to_retrieve = ordered_keys[offset:]

    return ResponseWrapper([diffs[key] for key in keys_to_retrieve])

def get_dummy_users(*args, **kwargs):
    return ResponseWrapper(json.loads('''
        {
          "0" : {
            "phid"     : "PHID-USER-froe3pl0phoe6lap2oer",
            "userName" : "alice",
            "realName" : "Alice In Wonderland",
            "uri"      : "http:\/\/www.example.com\/p\/aron\/",
            "roles"    : [
              "verified",
              "approved",
              "activated"
            ]
          },
          "1" : {
            "phid"     : "PHID-USER-thi47riaglakoejlabla",
            "userName" : "bob",
            "realName" : "Bob Bobberann",
            "uri"      : "http:\/\/www.example.com\/p\/bob\/",
            "roles"    : [
              "verified",
              "approved",
              "activated"
            ]
          },
          "2" : {
            "phid"     : "PHID-USER-c0ieboustiagouxlex90",
            "userName" : "carol",
            "realName" : "Carol Noel",
            "uri"      : "http:\/\/www.example.com\/p\/carol\/",
            "roles"    : [
              "verified",
              "approved",
              "activated"
            ]
          }
        }
    ''').values())

def get_dummy_projects(*args, **kwargs):
    return ResponseWrapper(json.loads('''
        {
          "data"    : {
            "PHID-PROJ-hh55htv4ejajjtssl63x" : {
              "id"           : "14",
              "phid"         : "PHID-PROJ-hh55htv4ejajjtssl63x",
              "name"         : "Initech",
              "members"      : [
                "PHID-USER-7ij42wfj575ujswtrie3",
                "PHID-USER-tplkspa2wre33aia64jj",
                "PHID-USER-nlmzlxfljlydy4sxxgs6"
              ],
              "slugs"        : [
                "initech"
              ],
              "dateCreated"  : "1400605314",
              "dateModified" : "1409866109"
            },
            "PHID-PROJ-tsxr7ui2y7ehkgnbjv3d" : {
              "id"           : "33",
              "phid"         : "PHID-PROJ-tsxr7ui2y7ehkgnbjv3d",
              "name"         : "Acme Inc.",
              "members"      : [
                "PHID-USER-7ij42wfj575ujswtrie3",
                "PHID-USER-tplkspa2wre33aia64jj"
              ],
              "slugs"        : [
                "acme"
              ],
              "dateCreated"  : "1402410736",
              "dateModified" : "1409866111"
            },
            "PHID-PROJ-lp7tvyjqf44eaxvvgra5" : {
              "id"           : "26",
              "phid"         : "PHID-PROJ-lp7tvyjqf44eaxvvgra5",
              "name"         : "Sirius Cybernetics",
              "members"      : [
                "PHID-USER-7ij42wfj575ujswtrie3",
                "PHID-USER-tplkspa2wre33aia64jj"
              ],
              "slugs"        : [
                "sirius"
              ],
              "dateCreated"  : "1401291083",
              "dateModified" : "1412700294"
            },
            "PHID-PROJ-bsw4glqdqvhi6zeahhrl" : {
              "id"           : "6",
              "phid"         : "PHID-PROJ-bsw4glqdqvhi6zeahhrl",
              "name"         : "Cyberdyne Systems",
              "members"      : [
                "PHID-USER-nlmzlxfljlydy4sxxgs6",
                "PHID-USER-fyjob3zmv3ouujpo7qq4",
                "PHID-USER-vp3mniwkkxgrofshbvvx",
                "PHID-USER-bjib42skttwqu6aof72j",
                "PHID-USER-wpbqwbdyyz3oebmarkwm",
                "PHID-USER-tplkspa2wre33aia64jj"
              ],
              "slugs"        : [
                "cyberdyne"
              ],
              "dateCreated"  : "1398434918",
              "dateModified" : "1405951963"
            },
            "PHID-PROJ-wytwyk4lk4rhydo2rtjw" : {
              "id"           : "13",
              "phid"         : "PHID-PROJ-wytwyk4lk4rhydo2rtjw",
              "name"         : "LexCorp",
              "members"      : [
                "PHID-USER-7ij42wfj575ujswtrie3",
                "PHID-USER-xthsstho7huexsoinsmh",
                "PHID-USER-nlmzlxfljlydy4sxxgs6",
                "PHID-USER-tplkspa2wre33aia64jj"
              ],
              "slugs"        : [
                "lex"
              ],
              "dateCreated"  : "1400600806",
              "dateModified" : "1409866116"
            }
          },
          "slugMap" : [],
          "cursor"  : {
            "limit"  : 5,
            "after"  : null,
            "before" : null
          }
        }
    '''))

def get_dummy_repos(*args, **kwargs):
    return ResponseWrapper(json.loads('''
        {
          "0"  : {
            "id"          : "27",
            "name"        : "Initech",
            "phid"        : "PHID-REPO-gik7kxdxot7e7ejnt4ws",
            "callsign"    : "INI",
            "monogram"    : "rINI",
            "vcs"         : "git",
            "uri"         : "http:\/\/www.example.com\/diffusion\/INI\/",
            "remoteURI"   : "git@github.com:example\/initech.git",
            "description" : "",
            "isActive"    : true,
            "isHosted"    : false,
            "isImporting" : false
          },
          "1"  : {
            "id"          : "26",
            "name"        : "Theme: Initech",
            "phid"        : "PHID-REPO-sdubuuo22fi7anftow42",
            "callsign"    : "TINI",
            "monogram"    : "rTINI",
            "vcs"         : "git",
            "uri"         : "http:\/\/www.example.com\/diffusion\/TINI\/",
            "remoteURI"   : "git@github.com:example\/theme-initech.git",
            "description" : null,
            "isActive"    : true,
            "isHosted"    : false,
            "isImporting" : false
          },
          "2"  : {
            "id"          : "25",
            "name"        : "Terminator Firmware",
            "phid"        : "PHID-REPO-yjgfviaqnoshuyrb6rla",
            "callsign"    : "TFW",
            "monogram"    : "rTFW",
            "vcs"         : "git",
            "uri"         : "http:\/\/www.example.com\/diffusion\/TFW\/",
            "remoteURI"   : "git@github.com:example\/terminator-firmware.git",
            "description" : null,
            "isActive"    : true,
            "isHosted"    : false,
            "isImporting" : false
          },
          "3"  : {
            "id"          : "24",
            "name"        : "Anvil",
            "phid"        : "PHID-REPO-plwv2eqmm6s4pxogjjyt",
            "callsign"    : "ANV",
            "monogram"    : "rANV",
            "vcs"         : "git",
            "uri"         : "http:\/\/www.example.com\/diffusion\/ANV\/",
            "remoteURI"   : "git@github.com:example\/Anvil.git",
            "description" : null,
            "isActive"    : true,
            "isHosted"    : false,
            "isImporting" : false
          },
          "4"  : {
            "id"          : "23",
            "name"        : "Towel",
            "phid"        : "PHID-REPO-x3ju6q2lmdlxlbpn2lxu",
            "callsign"    : "TOW",
            "monogram"    : "rTOW",
            "vcs"         : "git",
            "uri"         : "http:\/\/www.example.com\/diffusion\/TOW\/",
            "remoteURI"   : "git@github.com:example\/towel.git",
            "description" : null,
            "isActive"    : true,
            "isHosted"    : false,
            "isImporting" : false
          }
        }
    ''').values())

def get_dummy_diffs(order=None, **kwargs):
    if order is None:
        return json.loads('''
            {
              "0" : {
                "id"                  : "1466",
                "phid"                : "PHID-DREV-evimsdp6ol7ydgbh4hna",
                "title"               : "Added Admin Panel link in footer for admin users",
                "uri"                 : "http:\/\/www.example.com\/D1466",
                "dateCreated"         : "1426608361",
                "dateModified"        : "1426608651",
                "authorPHID"          : "PHID-USER-c0ieboustiagouxlex90",
                "status"              : "3",
                "statusName"          : "Closed",
                "branch"              : null,
                "summary"             : "",
                "testPlan"            : "Manual testing",
                "lineCount"           : "34",
                "activeDiffPHID"      : "PHID-DIFF-dlf6bpapdeiijgr27zws",
                "diffs"               : [
                  "3902",
                  "3901",
                  "3900",
                  "3899"
                ],
                "commits"             : [
                  "PHID-CMIT-cbejshgj6itjjmtjsfra",
                  "PHID-CMIT-mxxgrcgqv7ha44hfjjkc",
                  "PHID-CMIT-satqvxojbzus4ogibl2p"
                ],
                "reviewers"           : [
                  "PHID-USER-thi47riaglakoejlabla"
                ],
                "ccs"                 : [
                  "PHID-USER-tplkspa2wre33aia64jj",
                  "PHID-USER-7ij42wfj575ujswtrie3"
                ],
                "hashes"              : [
                  [
                    "gtcm",
                    "00c9c65a5a52884b0d932e6da25f461d27174a3a"
                  ],
                  [
                    "gttr",
                    "0910f9fcd20de535a0b1018614e9ed2d1c118283"
                  ],
                  [
                    "gtcm",
                    "9931e380a949cc08fa32ad512a9733f8e9e28681"
                  ],
                  [
                    "gttr",
                    "2337ed4548f4a625f30b1b432cf5e64384549977"
                  ]
                ],
                "auxiliary"           : {
                  "phabricator:projects"   : [],
                  "phabricator:depends-on" : []
                },
                "arcanistProjectPHID" : null,
                "repositoryPHID"      : "PHID-REPO-plwv2eqmm6s4pxogjjyt"
              },
              "1" : {
                "id"                  : "1465",
                "phid"                : "PHID-DREV-bxdze45ass5m3fhsiji2",
                "title"               : "Re-enabled clicking outside of lightbox to close. Added a check for input and redactor-editor elements that creates a confirmation dialog upon close.",
                "uri"                 : "http:\/\/www.example.com\/D1465",
                "dateCreated"         : "1426605794",
                "dateModified"        : "1426606649",
                "authorPHID"          : "PHID-USER-froe3pl0phoe6lap2oer",
                "status"              : "3",
                "statusName"          : "Closed",
                "branch"              : null,
                "summary"             : "Refactored confirmOrClose into the hide method",
                "testPlan"            : "http:\/\/www.example.com\/dashboard - you'll have to log in to test as the login\/signup lightbox doesn't use the same JS.",
                "lineCount"           : "48",
                "activeDiffPHID"      : "PHID-DIFF-6sjnqtieylr7epkb3rbo",
                "diffs"               : [
                  "3898",
                  "3897",
                  "3896"
                ],
                "commits"             : [
                  "PHID-CMIT-2djmq36o2hphotb6bbx4",
                  "PHID-CMIT-6lnokxfja3rvntokhl3r",
                  "PHID-CMIT-jxymky3muc3ljlv7tjo6",
                  "PHID-CMIT-ltwyztf64ssyxobx3kdm"
                ],
                "reviewers"           : [
                  "PHID-USER-c0ieboustiagouxlex90"
                ],
                "ccs"                 : [
                  "PHID-USER-tplkspa2wre33aia64jj",
                  "PHID-USER-7ij42wfj575ujswtrie3"
                ],
                "hashes"              : [
                  [
                    "gtcm",
                    "0bae47d8b623ebf3a89c33455c4009c2dca9be30"
                  ],
                  [
                    "gttr",
                    "05c92cd1b102314f04f040928dc625c022cd9e22"
                  ],
                  [
                    "gtcm",
                    "de500638d082414024510b33b73c06e3d8bc4601"
                  ],
                  [
                    "gttr",
                    "dd753b8045dab176e22e6acb188ff9305a83fe63"
                  ],
                  [
                    "gtcm",
                    "ca5140722e3e5c21f1510312459a5052fc5d90aa"
                  ],
                  [
                    "gttr",
                    "923f77ec361e8b244909b245caf553d775d4996d"
                  ]
                ],
                "auxiliary"           : {
                  "phabricator:projects"   : [],
                  "phabricator:depends-on" : []
                },
                "arcanistProjectPHID" : null,
                "repositoryPHID"      : "PHID-REPO-plwv2eqmm6s4pxogjjyt"
              },
              "2" : {
                "id"                  : "1464",
                "phid"                : "PHID-DREV-qmwnwadjiwyr4f4jn7vx",
                "title"               : "Fixed failing unit tests and updated code based on tests so that getThumbnail in Pitch conforms to convention of getThumbnail interfaced defined in HasThumbTrait",
                "uri"                 : "http:\/\/www.example.com\/D1464",
                "dateCreated"         : "1426538708",
                "dateModified"        : "1426604017",
                "authorPHID"          : "PHID-USER-thi47riaglakoejlabla",
                "status"              : "3",
                "statusName"          : "Closed",
                "branch"              : null,
                "summary"             : "",
                "testPlan"            : "glance over, or even better, arc patch and run phpunit at command line",
                "lineCount"           : "109",
                "activeDiffPHID"      : "PHID-DIFF-kuglybb2azqmiuax3rus",
                "diffs"               : [
                  "3895",
                  "3894",
                  "3893",
                  "3891"
                ],
                "commits"             : [
                  "PHID-CMIT-iola6rruxsiqzm3yjisv",
                  "PHID-CMIT-l2ynadg3djlpa2z7gjhw",
                  "PHID-CMIT-xzxjgv6u4np6bf6nwgdj",
                  "PHID-CMIT-yjty6thlu2js2kh7stjt"
                ],
                "reviewers"           : [
                  "PHID-USER-c0ieboustiagouxlex90"
                ],
                "ccs"                 : [
                  "PHID-USER-wpbqwbdyyz3oebmarkwm",
                  "PHID-USER-tplkspa2wre33aia64jj",
                  "PHID-USER-7ij42wfj575ujswtrie3",
                  "PHID-USER-xthsstho7huexsoinsmh"
                ],
                "hashes"              : [
                  [
                    "gtcm",
                    "73f2ba59edcfe53262504c4f533c540f953b8c71"
                  ],
                  [
                    "gttr",
                    "f4fe9af47c8230db233416e16d3d9a153b25f83f"
                  ],
                  [
                    "gtcm",
                    "7ec93e5fc6d022d2dbd8998771a6ec2232849fe0"
                  ],
                  [
                    "gttr",
                    "d5abf0657488c52d5411f77298a4b5abbd1f19fa"
                  ],
                  [
                    "gtcm",
                    "21acffc6bb519f88742ccaf0d880b9df9275def9"
                  ],
                  [
                    "gttr",
                    "2d3cc415245113d90ac03ee9f847f0c7c068e143"
                  ]
                ],
                "auxiliary"           : {
                  "phabricator:projects"   : [],
                  "phabricator:depends-on" : []
                },
                "arcanistProjectPHID" : null,
                "repositoryPHID"      : "PHID-REPO-plwv2eqmm6s4pxogjjyt"
              },
              "3" : {
                "id"                  : "1463",
                "phid"                : "PHID-DREV-fpozavsjbpzqrmbegkir",
                "title"               : "Updated missing or deprecated class selectors causing portfolio touchswipe to break",
                "uri"                 : "http:\/\/www.example.com\/D1463",
                "dateCreated"         : "1426537711",
                "dateModified"        : "1426537900",
                "authorPHID"          : "PHID-USER-froe3pl0phoe6lap2oer",
                "status"              : "3",
                "statusName"          : "Closed",
                "branch"              : null,
                "summary"             : "",
                "testPlan"            : "Manual",
                "lineCount"           : "10",
                "activeDiffPHID"      : "PHID-DIFF-7jwsrhnj3jnhluihz7me",
                "diffs"               : [
                  "3890",
                  "3889",
                  "3888",
                  "3887",
                  "3886"
                ],
                "commits"             : [
                  "PHID-CMIT-5cvjk7hsdrfojmbnevqh",
                  "PHID-CMIT-64qe3zmiue6kbfo4qiiv",
                  "PHID-CMIT-7sybzgtorqi6u6ngh7je",
                  "PHID-CMIT-inxwdrzdksqxsrz6kjjm"
                ],
                "reviewers"           : [
                  "PHID-USER-thi47riaglakoejlabla"
                ],
                "ccs"                 : [
                  "PPHID-USER-thi47riaglakoejlabla",
                  "PHID-USER-7ij42wfj575ujswtrie3"
                ],
                "hashes"              : [
                  [
                    "gtcm",
                    "fc48dfb3d22170655aebf84de62f6f43dc42c720"
                  ],
                  [
                    "gttr",
                    "638fa8e5066288032c76355888e57d608ed1c197"
                  ],
                  [
                    "gtcm",
                    "ad532b952e1924730f42ff111f670f5fc7a75d29"
                  ],
                  [
                    "gttr",
                    "51c713c9f4ca1df0ac8698f6f02b87b372c7dc24"
                  ],
                  [
                    "gtcm",
                    "407c81d7409288a77b71e33c008ad268acdacab5"
                  ],
                  [
                    "gttr",
                    "b49b3b084506c434c3e06885e89fab646fb27629"
                  ]
                ],
                "auxiliary"           : {
                  "phabricator:projects"   : [],
                  "phabricator:depends-on" : []
                },
                "arcanistProjectPHID" : null,
                "repositoryPHID"      : "PHID-REPO-plwv2eqmm6s4pxogjjyt"
              },
              "4" : {
                "id"                  : "1462",
                "phid"                : "PHID-DREV-ofkdf6mx4dpda4gftzyb",
                "title"               : "Re-enabled clicking outside of lightbox to close. Added a check for input and redactor-editor elements that creates a confirmation dialog upon close.",
                "uri"                 : "http:\/\/www.example.com\/D1462",
                "dateCreated"         : "1426536587",
                "dateModified"        : "1426606010",
                "authorPHID"          : "PHID-USER-thi47riaglakoejlabla",
                "status"              : "4",
                "statusName"          : "Abandoned",
                "branch"              : "T2627",
                "summary"             : "",
                "testPlan"            : "http:\/\/www.example.com\/dashboard - you'll have to log in to test as the login\/signup lightbox doesn't use the same JS.",
                "lineCount"           : "48",
                "activeDiffPHID"      : "PHID-DIFF-7mi66mebatdnv4fnjhxy",
                "diffs"               : [
                  "3885"
                ],
                "commits"             : [],
                "reviewers"           : [
                  "PHID-USER-froe3pl0phoe6lap2oer",
                  "PHID-USER-c0ieboustiagouxlex90"
                ],
                "ccs"                 : [
                  "PHID-USER-tplkspa2wre33aia64jj",
                  "PHID-USER-7ij42wfj575ujswtrie3"
                ],
                "hashes"              : [
                  [
                    "gtcm",
                    "38e9a1dd0a727290e118d0dd8b1851227745cc87"
                  ],
                  [
                    "gttr",
                    "156e9da8ce76cc25254070f9bdbed181f31d4b1b"
                  ]
                ],
                "auxiliary"           : {
                  "phabricator:projects"   : [],
                  "phabricator:depends-on" : []
                },
                "arcanistProjectPHID" : null,
                "repositoryPHID"      : "PHID-REPO-plwv2eqmm6s4pxogjjyt"
              }
            }
        ''')

    else:
        return json.loads('''
            {
              "0" : {
                "id"                  : "1466",
                "phid"                : "PHID-DREV-evimsdp6ol7ydgbh4hna",
                "title"               : "Added Admin Panel link in footer for admin users",
                "uri"                 : "http:\/\/www.example.com\/D1466",
                "dateCreated"         : "1426608361",
                "dateModified"        : "1426608651",
                "authorPHID"          : "PHID-USER-c0ieboustiagouxlex90",
                "status"              : "3",
                "statusName"          : "Closed",
                "branch"              : null,
                "summary"             : "",
                "testPlan"            : "Manual testing",
                "lineCount"           : "34",
                "activeDiffPHID"      : "PHID-DIFF-dlf6bpapdeiijgr27zws",
                "diffs"               : [
                  "3902",
                  "3901",
                  "3900",
                  "3899"
                ],
                "commits"             : [
                  "PHID-CMIT-cbejshgj6itjjmtjsfra",
                  "PHID-CMIT-mxxgrcgqv7ha44hfjjkc",
                  "PHID-CMIT-satqvxojbzus4ogibl2p"
                ],
                "reviewers"           : [
                  "PHID-USER-thi47riaglakoejlabla"
                ],
                "ccs"                 : [
                  "PHID-USER-tplkspa2wre33aia64jj",
                  "PHID-USER-7ij42wfj575ujswtrie3"
                ],
                "hashes"              : [
                  [
                    "gtcm",
                    "00c9c65a5a52884b0d932e6da25f461d27174a3a"
                  ],
                  [
                    "gttr",
                    "0910f9fcd20de535a0b1018614e9ed2d1c118283"
                  ],
                  [
                    "gtcm",
                    "9931e380a949cc08fa32ad512a9733f8e9e28681"
                  ],
                  [
                    "gttr",
                    "2337ed4548f4a625f30b1b432cf5e64384549977"
                  ]
                ],
                "auxiliary"           : {
                  "phabricator:projects"   : [],
                  "phabricator:depends-on" : []
                },
                "arcanistProjectPHID" : null,
                "repositoryPHID"      : "PHID-REPO-plwv2eqmm6s4pxogjjyt"
              },
              "1" : {
                "id"                  : "1465",
                "phid"                : "PHID-DREV-bxdze45ass5m3fhsiji2",
                "title"               : "Re-enabled clicking outside of lightbox to close. Added a check for input and redactor-editor elements that creates a confirmation dialog upon close.",
                "uri"                 : "http:\/\/www.example.com\/D1465",
                "dateCreated"         : "1426605794",
                "dateModified"        : "1426606649",
                "authorPHID"          : "PHID-USER-froe3pl0phoe6lap2oer",
                "status"              : "3",
                "statusName"          : "Closed",
                "branch"              : null,
                "summary"             : "Refactored confirmOrClose into the hide method",
                "testPlan"            : "http:\/\/www.example.com\/dashboard - you'll have to log in to test as the login\/signup lightbox doesn't use the same JS.",
                "lineCount"           : "48",
                "activeDiffPHID"      : "PHID-DIFF-6sjnqtieylr7epkb3rbo",
                "diffs"               : [
                  "3898",
                  "3897",
                  "3896"
                ],
                "commits"             : [
                  "PHID-CMIT-2djmq36o2hphotb6bbx4",
                  "PHID-CMIT-6lnokxfja3rvntokhl3r",
                  "PHID-CMIT-jxymky3muc3ljlv7tjo6",
                  "PHID-CMIT-ltwyztf64ssyxobx3kdm"
                ],
                "reviewers"           : [
                  "PHID-USER-c0ieboustiagouxlex90"
                ],
                "ccs"                 : [
                  "PHID-USER-thi47riaglakoejlabla",
                  "PHID-USER-7ij42wfj575ujswtrie3"
                ],
                "hashes"              : [
                  [
                    "gtcm",
                    "0bae47d8b623ebf3a89c33455c4009c2dca9be30"
                  ],
                  [
                    "gttr",
                    "05c92cd1b102314f04f040928dc625c022cd9e22"
                  ],
                  [
                    "gtcm",
                    "de500638d082414024510b33b73c06e3d8bc4601"
                  ],
                  [
                    "gttr",
                    "dd753b8045dab176e22e6acb188ff9305a83fe63"
                  ],
                  [
                    "gtcm",
                    "ca5140722e3e5c21f1510312459a5052fc5d90aa"
                  ],
                  [
                    "gttr",
                    "923f77ec361e8b244909b245caf553d775d4996d"
                  ]
                ],
                "auxiliary"           : {
                  "phabricator:projects"   : [],
                  "phabricator:depends-on" : []
                },
                "arcanistProjectPHID" : null,
                "repositoryPHID"      : "PHID-REPO-plwv2eqmm6s4pxogjjyt"
              },
              "2" : {
                "id"                  : "1460",
                "phid"                : "PHID-DREV-dhxm3v6pujqh7ixmfhnx",
                "title"               : "Sync channel status with campaign status",
                "uri"                 : "http:\/\/www.example.com\/D1460",
                "dateCreated"         : "1426529001",
                "dateModified"        : "1426606612",
                "authorPHID"          : "PHID-USER-thi47riaglakoejlabla",
                "status"              : "3",
                "statusName"          : "Closed",
                "branch"              : "T3043",
                "summary"             : "Update yoyodyne script to sync channel Published, Awaiting, and Rejected statuses to campaign status.",
                "testPlan"            : "Alice and Bob tested",
                "lineCount"           : "58",
                "activeDiffPHID"      : "PHID-DIFF-62kjerbubprnetr6gun7",
                "diffs"               : [
                  "3882"
                ],
                "commits"             : [],
                "reviewers"           : [
                  "PHID-USER-froe3pl0phoe6lap2oer",
                  "PHID-USER-c0ieboustiagouxlex90"
                ],
                "ccs"                 : [
                  "PHID-USER-tplkspa2wre33aia64jj",
                  "PHID-USER-7ij42wfj575ujswtrie3"
                ],
                "hashes"              : [
                  [
                    "gtcm",
                    "d6ffc31cb8c3781d91385696208a0dde243a0f88"
                  ],
                  [
                    "gttr",
                    "f6713e4169d3aa2144be3d887b9d6fb70e4f3c80"
                  ]
                ],
                "auxiliary"           : {
                  "phabricator:projects"   : [],
                  "phabricator:depends-on" : []
                },
                "arcanistProjectPHID" : null,
                "repositoryPHID"      : null
              },
              "3" : {
                "id"                  : "1462",
                "phid"                : "PHID-DREV-ofkdf6mx4dpda4gftzyb",
                "title"               : "Re-enabled clicking outside of lightbox to close. Added a check for input and redactor-editor elements that creates a confirmation dialog upon close.",
                "uri"                 : "http:\/\/www.example.com\/D1462",
                "dateCreated"         : "1426536587",
                "dateModified"        : "1426606010",
                "authorPHID"          : "PHID-USER-thi47riaglakoejlabla",
                "status"              : "4",
                "statusName"          : "Abandoned",
                "branch"              : "T2627",
                "summary"             : "",
                "testPlan"            : "http:\/\/www.example.com\/dashboard - you'll have to log in to test as the login\/signup lightbox doesn't use the same JS.",
                "lineCount"           : "48",
                "activeDiffPHID"      : "PHID-DIFF-7mi66mebatdnv4fnjhxy",
                "diffs"               : [
                  "3885"
                ],
                "commits"             : [],
                "reviewers"           : [
                  "PHID-USER-froe3pl0phoe6lap2oer",
                  "PHID-USER-c0ieboustiagouxlex90"
                ],
                "ccs"                 : [
                  "PHID-USER-tplkspa2wre33aia64jj",
                  "PHID-USER-7ij42wfj575ujswtrie3"
                ],
                "hashes"              : [
                  [
                    "gtcm",
                    "38e9a1dd0a727290e118d0dd8b1851227745cc87"
                  ],
                  [
                    "gttr",
                    "156e9da8ce76cc25254070f9bdbed181f31d4b1b"
                  ]
                ],
                "auxiliary"           : {
                  "phabricator:projects"   : [],
                  "phabricator:depends-on" : []
                },
                "arcanistProjectPHID" : null,
                "repositoryPHID"      : "PHID-REPO-plwv2eqmm6s4pxogjjyt"
              },
              "4" : {
                "id"                  : "1464",
                "phid"                : "PHID-DREV-qmwnwadjiwyr4f4jn7vx",
                "title"               : "Fixed failing unit tests and updated code based on tests so that getThumbnail in Pitch conforms to convention of getThumbnail interfaced defined in HasThumbTrait",
                "uri"                 : "http:\/\/www.example.com\/D1464",
                "dateCreated"         : "1426538708",
                "dateModified"        : "1426604017",
                "authorPHID"          : "PHID-USER-froe3pl0phoe6lap2oer",
                "status"              : "3",
                "statusName"          : "Closed",
                "branch"              : null,
                "summary"             : "",
                "testPlan"            : "glance over, or even better, arc patch and run phpunit at command line",
                "lineCount"           : "109",
                "activeDiffPHID"      : "PHID-DIFF-kuglybb2azqmiuax3rus",
                "diffs"               : [
                  "3895",
                  "3894",
                  "3893",
                  "3891"
                ],
                "commits"             : [
                  "PHID-CMIT-iola6rruxsiqzm3yjisv",
                  "PHID-CMIT-l2ynadg3djlpa2z7gjhw",
                  "PHID-CMIT-xzxjgv6u4np6bf6nwgdj",
                  "PHID-CMIT-yjty6thlu2js2kh7stjt"
                ],
                "reviewers"           : [
                  "PHID-USER-c0ieboustiagouxlex90",
                  "PHID-USER-thi47riaglakoejlabla"
                ],
                "ccs"                 : [
                  "PHID-USER-tplkspa2wre33aia64jj",
                  "PHID-USER-wpbqwbdyyz3oebmarkwm",
                  "PHID-USER-7ij42wfj575ujswtrie3",
                  "PHID-USER-xthsstho7huexsoinsmh"
                ],
                "hashes"              : [
                  [
                    "gtcm",
                    "73f2ba59edcfe53262504c4f533c540f953b8c71"
                  ],
                  [
                    "gttr",
                    "f4fe9af47c8230db233416e16d3d9a153b25f83f"
                  ],
                  [
                    "gtcm",
                    "7ec93e5fc6d022d2dbd8998771a6ec2232849fe0"
                  ],
                  [
                    "gttr",
                    "d5abf0657488c52d5411f77298a4b5abbd1f19fa"
                  ],
                  [
                    "gtcm",
                    "21acffc6bb519f88742ccaf0d880b9df9275def9"
                  ],
                  [
                    "gttr",
                    "2d3cc415245113d90ac03ee9f847f0c7c068e143"
                  ]
                ],
                "auxiliary"           : {
                  "phabricator:projects"   : [],
                  "phabricator:depends-on" : []
                },
                "arcanistProjectPHID" : null,
                "repositoryPHID"      : "PHID-REPO-plwv2eqmm6s4pxogjjyt"
              }
            }
        ''')