# pynet_class
The 'Kirk Buyers Python Course'



./step6.py

======================
list from file: var/yaml_file.yml in YAML data_format:
======================
---
- 0
- 1
- 2
- 3
- 4
- 5
- 6
- 7
- 8
- 9
- key1:
  - 0
  - 1
  - 2
  - 3
  key2: some_value_for_key2

======================
list from file: var/yaml_file.yml in pretty_print native python
======================
[0,
 1,
 2,
 3,
 4,
 5,
 6,
 7,
 8,
 9,
 {'key1': [0,
           1,
           2,
           3],
  'key2': 'some_value_for_key2'}]



./step7.py

======================
list from file: var/json_file.json in JSON data_format:
======================
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, {"key2": "some_value_for_key2", "key1": [0, 1, 2, 3]}]
======================
list from file: var/json_file.json in pretty_print native python
======================
[0,
 1,
 2,
 3,
 4,
 5,
 6,
 7,
 8,
 9,
 {u'key1': [0,
            1,
            2,
            3],
  u'key2': u'some_value_for_key2'}]



./step8.py ## steps 8 - 10

>> crypto objects with 'crypto map CRYPTO':
==========================
crypto map CRYPTO 10 ipsec-isakmp 
==========================
     set peer 1.1.1.1
     set transform-set AES-SHA 
     set pfs group5
     match address VPN-TEST1

==========================
crypto map CRYPTO 20 ipsec-isakmp 
==========================
     set peer 2.2.2.1
     set transform-set AES-SHA 
     set pfs group2
     match address VPN-TEST2

==========================
crypto map CRYPTO 30 ipsec-isakmp 
==========================
     set peer 3.3.3.1
     set transform-set AES-SHA 
     set pfs group2
     match address VPN-TEST3

==========================
crypto map CRYPTO 40 ipsec-isakmp 
==========================
     set peer 4.4.4.1
     set transform-set AES-SHA 
     set pfs group5
     match address VPN-TEST4

==========================
crypto map CRYPTO 50 ipsec-isakmp 
==========================
     set peer 5.5.5.1
     set transform-set 3DES-SHA 
     set pfs group5
     match address VPN-TEST5

>> crypto objects with 'pfs group2' children:
==========================
crypto map CRYPTO 20 ipsec-isakmp 
==========================
==========================
crypto map CRYPTO 30 ipsec-isakmp 
==========================

>> objects with no children using AES:
==========================
crypto map CRYPTO 50 ipsec-isakmp 
 set transform-set 3DES-SHA 
==========================

