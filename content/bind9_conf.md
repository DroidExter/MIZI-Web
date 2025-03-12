# Deployment of BIND 9
In this guide, I describe the deployment of BIND 9 as an authoritative nameserver. The installation was performed on a device running Ubuntu 24.04.1 LTS.

## Installation and Configuration
To start, I updated the apt cache and installed BIND 9:

```bash
sudo apt update -y && sudo apt install bind9 -y
```

Then, I configured the forwarders parameter in the file /etc/bind/named.conf.options, which specifies where DNS queries will be forwarded if my server is unable to resolve them (IPv6 addresses for Cloudflare primary and secondary DNS were used) [^cloudflare_ip]. Inside the listen-on-v6 parameter, I set the IPv6 loopback (::1) and the device's global unicast address (which can be obtained, for example, using the command `ip -6 a`):

```c
options {
        directory "/var/cache/bind";

        // If there is a firewall between you and nameservers you want
        // to talk to, you may need to fix the firewall to allow multiple
        // ports to talk.  See http://www.kb.cert.org/vuls/id/800113

        // If your ISP provided one or more IP addresses for stable
        // nameservers, you probably want to use them as forwarders.
        // Uncomment the following block, and insert the addresses replacing
        // the all-0's placeholder.

        // forwarders {
        //      0.0.0.0;
        // };

        //========================================================================
        // If BIND logs error messages about the root key being expired,
        // you will need to update your keys.  See https://www.isc.org/bind-keys
        //========================================================================

        forwarders {
            2606:4700:4700::1111;
            2606:4700:4700::1001;
        };
        dnssec-validation no;
        listen-on-v6 { ::1; 2001:718:1001:2cf:20c:29ff:fe1d:e949; };
};
```

By default, it should be set to listen-on-v6 { any; }, meaning that BIND9 will listen on all IPv6 network interfaces.

Next, it was necessary to define the domain for the zone, its type, and the path to the file in the named.conf.local file, which I would create later:

```c
//
// Do any local configuration here
//

// Consider adding the 1918 zones here, if they are not used in your
// organization
//include "/etc/bind/zones.rfc1918";

zone "examdomain.com" {
    type master;
    file "/etc/bind/db.examdomain.com";
};
```

For this zone, I created the file db.examdomain.com in the /etc/bind/ directory and listed the appropriate parameters and individual DNS records:

```
$TTL 3600    ; default TTL for zone

@ IN SOA ns1.examdomain.com. hostmaster.examdomain.com. (
    2025022201 ; serial number
    12h        ; refresh
    15m        ; update retry
    3w         ; expiry
    2h         ; minimum
)

        IN  NS  ns1.examdomain.com.

ns1     IN  AAAA    2001:718:1001:2cf:20c:29ff:fe1d:e949

vir31   IN  AAAA    2001:718:1001:2cf:20c:29ff:fe8c:3229
vir32   IN  AAAA    2001:718:1001:2cf:20c:29ff:fe7c:dc5a
vir33   IN  AAAA    2001:718:1001:2cf:20c:29ff:fe1d:e949
vir34   IN  AAAA    2001:718:1001:2cf:20c:29ff:fe7c:9e10
vir35   IN  AAAA    2001:718:1001:2cf:20c:29ff:fe09:3131
vir36   IN  AAAA    2001:718:1001:2cf:20c:29ff:fef8:6c08
vir37   IN  AAAA    2001:718:1001:2cf:20c:29ff:fe91:ed49
vir38   IN  AAAA    2001:718:1001:2cf:20c:29ff:fed9:e03f
vir39   IN  AAAA    2001:718:1001:2cf:20c:29ff:fea5:496b
vir40   IN  AAAA    2001:718:1001:2cf:20c:29ff:fe21:6701
vir41   IN  AAAA    2001:718:1001:2cf:20c:29ff:fecd:d97a
vir42   IN  AAAA    2001:718:1001:2cf:20c:29ff:fe15:a285
vir43   IN  AAAA    2001:718:1001:2cf:20c:29ff:fefc:b0ef
vir44   IN  AAAA    2001:718:1001:2cf:20c:29ff:fedc:7147
vir45   IN  AAAA    2001:718:1001:2cf:20c:29ff:fe4d:bad2
vir46   IN  AAAA    2001:718:1001:2cf:20c:29ff:fe89:abc4
vir47   IN  AAAA    2001:718:1001:2cf:20c:29ff:feba:9820
vir48   IN  AAAA    2001:718:1001:2cf:20c:29ff:fe17:d7cf
vir49   IN  AAAA    2001:718:1001:2cf:20c:29ff:fe2a:b738
vir50   IN  AAAA    2001:718:1001:2cf:20c:29ff:fef1:1be7
vir51   IN  AAAA    2001:718:1001:2cf:20c:29ff:febe:d077
vir52   IN  AAAA    2001:718:1001:2cf:20c:29ff:fef6:6321
vir53   IN  AAAA    2001:718:1001:2cf:20c:29ff:fe16:438f
```

At the beginning of the file, I set the TTL (Time To Live), which defines the time (in seconds) for which DNS servers can cache records from this zone. I also added the SOA (Start of Authority) record, which must be present in every zone. Here are the meanings of the individual parameters:

- **@** - placeholder for the domain (examdomain.com, as set in the named.conf.local file)
- **IN** - in DNS records, stands for Internet Class. It is used in almost all common cases.
- **SOA** - indicates that this is an SOA record.
- **ns1.examdomain.com.** - Primary DNS server for this domain. A dot is used at the end to indicate that it is an absolute domain path. The name "ns1" usually refers to the primary nameserver.
- **hostmaster.examdomain.com.** - The email address of the administrator, with a dot (.) instead of @. In my case, it is just a placeholder.
- **serial number** - Serves as the version identifier for this configuration file, typically in the format YYYYMMDDNN, where YYYYMMDD denotes the year, month, and day, and NN could indicate the change count for that day (typically starting at 01).
- **refresh** - How often secondary servers should check for changes.
- **update retry** - How quickly they should retry if the first attempt fails.
- **expiry** - How long secondary servers can consider the data valid if the primary server fails.
- **minimum** - The minimum TTL for negative responses (e.g., when a domain does not exist).

Next, I added the NS (Name Server) record IN NS ns1.examdomain.com., where it is necessary to use the absolute DNS path ending with a dot. There can be multiple NS records in a zone, with additional servers functioning as secondary ones.

In the last part, I added records for NS and each virtual machine (vir31-53) assigned to the *PCN I* subject, using **AAAA** records, which are used for IPv6 addresses. For IPv4, **A** records are used.

To apply the changes, it is necessary to restart the service:

```bash
sudo service bind9 restart
```

To verify if the service is running:

```bash
sudo service bind9 status
```
```
● named.service - BIND Domain Name Server
     Loaded: loaded (/usr/lib/systemd/system/named.service; enabled; preset: enabled)
     Active: active (running) since Tue 2025-02-25 16:41:20 UTC; 1s ago
       Docs: man:named(8)
   Main PID: 124616 (named)
     Status: "running"
      Tasks: 6 (limit: 2276)
     Memory: 5.7M (peak: 6.1M)
        CPU: 17ms
     CGroup: /system.slice/named.service
             └─124616 /usr/sbin/named -f -u bind

Feb 25 16:41:20 studentvirtual033 named[124616]: command channel listening on ::1#953
Feb 25 16:41:20 studentvirtual033 named[124616]: managed-keys-zone: loaded serial 5
Feb 25 16:41:20 studentvirtual033 named[124616]: zone 255.in-addr.arpa/IN: loaded serial 1
Feb 25 16:41:20 studentvirtual033 named[124616]: zone 127.in-addr.arpa/IN: loaded serial 1
Feb 25 16:41:20 studentvirtual033 named[124616]: zone examdomain.com/IN: loaded serial 2025022201
Feb 25 16:41:20 studentvirtual033 named[124616]: zone localhost/IN: loaded serial 2
Feb 25 16:41:20 studentvirtual033 named[124616]: zone 0.in-addr.arpa/IN: loaded serial 1
Feb 25 16:41:20 studentvirtual033 named[124616]: all zones loaded
Feb 25 16:41:20 studentvirtual033 named[124616]: running
Feb 25 16:41:20 studentvirtual033 systemd[1]: Started named.service - BIND Domain Name Server.
```
For this configuration, I mainly drew from the information provided by ChatGPT. For more detailed configuration options, you can refer to the official web documentation at https://bind9.readthedocs.io/en/v9.20.6/.

## Verifying Functionality
To verify the functionality, it is necessary to configure the target IP address of the DNS server on a client device. This can be done on Ubuntu by adding a line in the /etc/systemd/resolved.conf file with the IP address of the DNS server, for example:
```
DNS=2001:718:1001:2cf:20c:29ff:fe1d:e949
```
Then, the service must be restarted:

```bash
sudo service systemd-resolved restart
```

After adding the DNS server, I tested DNS request handling on the client device using the dig command with the domain parameter for the device **vir33** and the AAAA parameter, which is used to query for the IPv6 address:

```bash
dig vir33.examdomain.com AAAA

; <<>> DiG 9.18.30-0ubuntu0.24.04.2-Ubuntu <<>> vir33.examdomain.com AAAA
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 52022
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 65494
;; QUESTION SECTION:
;vir33.examdomain.com.              IN      AAAA

;; ANSWER SECTION:
vir33.examdomain.com.       1708    IN      AAAA    2001:718:1001:2cf:20c:29ff:fe1d:e949

;; Query time: 0 msec
;; SERVER: 127.0.0.53#53(127.0.0.53) (UDP)
;; WHEN: Tue Feb 25 18:19:51 UTC 2025
;; MSG SIZE  rcvd: 73
```
A successful response for the DNS request should have an ANSWER section, containing the record with the required IPv6 address (in my case, `2001:718:1001:2cf:20c:29ff:fe1d:e949`).

## References
[^cloudflare_ip]: *Cloudflare Docs: IP addresses* [online]. [cit. 2025-02-25]. Available from: https://developers.cloudflare.com/1.1.1.1/ip-addresses/
