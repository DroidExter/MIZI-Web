# Knot DNS Deployment
In this guide, I describe the deployment of Knot DNS as an authoritative nameserver. The installation was carried out on a device running Ubuntu 24.04.1 LTS.

## Installation
Update apt cache and install prerequisites:

```bash
sudo apt update && sudo apt install apt-transport-https ca-certificates wget
```

Download and add the *CZ.NIC Labs* GPG key to /usr/share/keyrings/:

```bash
sudo wget -O /usr/share/keyrings/cznic-labs-pkg.gpg https://pkg.labs.nic.cz/gpg
```

Install the knot-dns repository:

```bash
echo "deb [signed-by=/usr/share/keyrings/cznic-labs-pkg.gpg] \
https://pkg.labs.nic.cz/knot-dns noble main" | \
sudo tee /etc/apt/sources.list.d/cznic-labs-knot-dns.list
```

Update apt cache and install knot:

```bash
sudo apt update && sudo apt install knot
```

Source: https://pkg.labs.nic.cz/doc/?project=knot-dns

## Configuration
To access the Knot directory, you need to be logged in as *root* or be part of the knot group. Therefore, I switched to the *root* user:

```bash
sudo su -
```

In the configuration file /etc/knot/knot.conf, I uncommented the listen parameter under the server section and added the global unicast IPv6 address of the device inside it (can be found using `ip -6 a`).

```yaml
server:
    rundir: "/run/knot"
    user: knot:knot
    automatic-acl: on
    listen: [ ::1@53, 2001:718:1001:2cf:20c:29ff:fe1d:e949@53 ]
```

Next, in the same file, I added the section for remote servers, where DNS queries that my server cannot resolve will be forwarded (IPv6 addresses were used for Cloudflare's primary and secondary DNS) [^cloudflare_ip]. I then added my domain `examdomain.com` to the zone section. When defining the domain, you must add a dot (.) at the end, indicating it's an absolute DNS path.

```yaml
remote:
  - id: primary
    address: 2606:4700:4700::1111@53

  - id: secondary
    address: 2606:4700:4700::1001@53

zone:
  - domain: examdomain.com.
```

In the /var/lib/knot/ directory, I created the file examdomain.com.zone, which defines my zone:

```
$ORIGIN examdomain.com.
examdomain.com.   SOA     ns1.examdomain.com. hostmaster.examdomain.com. 1 36000 600 864000 300

examdomain.com.   NS      ns1.examdomain.com.

ns1           AAAA    2001:db8:abcd:1234:5678:9abc:def0:5678
vir31         AAAA    2001:db8:abcd:1234:5678:9abc:def0:6789
vir32         AAAA    2001:db8:abcd:1234:5678:9abc:def0:789a
vir33         AAAA    2001:db8:abcd:1234:5678:9abc:def0:1234
vir34         AAAA    2001:db8:abcd:1234:5678:9abc:def0:abcd
vir35         AAAA    2001:db8:abcd:1234:5678:9abc:def0:5679
vir36         AAAA    2001:db8:abcd:1234:5678:9abc:def0:4321
vir37         AAAA    2001:db8:abcd:1234:5678:9abc:def0:678a
vir38         AAAA    2001:db8:abcd:1234:5678:9abc:def0:abcd
vir39         AAAA    2001:db8:abcd:1234:5678:9abc:def0:efgh
vir40         AAAA    2001:db8:abcd:1234:5678:9abc:def0:ijkl
vir41         AAAA    2001:db8:abcd:1234:5678:9abc:def0:mnop
vir42         AAAA    2001:db8:abcd:1234:5678:9abc:def0:qrst
vir43         AAAA    2001:db8:abcd:1234:5678:9abc:def0:uvwx
vir44         AAAA    2001:db8:abcd:1234:5678:9abc:def0:yzab
vir45         AAAA    2001:db8:abcd:1234:5678:9abc:def0:bcde
vir46         AAAA    2001:db8:abcd:1234:5678:9abc:def0:cdef
vir47         AAAA    2001:db8:abcd:1234:5678:9abc:def0:ghij
vir48         AAAA    2001:db8:abcd:1234:5678:9abc:def0:ijkl
vir49         AAAA    2001:db8:abcd:1234:5678:9abc:def0:lmn0
vir50         AAAA    2001:db8:abcd:1234:5678:9abc:def0:pqrs
vir51         AAAA    2001:db8:abcd:1234:5678:9abc:def0:uvw2
vir52         AAAA    2001:db8:abcd:1234:5678:9abc:def0:zabc
vir53         AAAA    2001:db8:abcd:1234:5678:9abc:def0:zxyz
```

The zone configuration for Knot DNS is very similar to BIND 9. Initially, I set $ORIGIN to examdomain.com., which specifies the default path for all relative DNS records. Then, I wrote the SOA (Start of Authority) record with the following parameters:

- **examdomain.com.** - absolute path to the domain
- **ns1.examdomain.com.** - absolute path for the primary DNS server for this domain.
- **hostmaster.examdomain.com.** Email address of the administrator, where the @ is replaced with a dot (.). In my case, this is just a placeholder.
- **1** - Version number of this configuration file
- **36000 600 864000** - Zone synchronization timers
- **300** - TTL for negative responses

Then, I added the NS (Name Server) record for examdomain.com. NS ns1.examdomain.com.. Just like in BIND 9, there can be multiple NS records in the zone, with additional servers acting as secondary.

In the last part, I have records for NS and each virtual machine intended for subject *PCN I*, where **AAAA** records are used for IPv6 addresses.

To apply the changes, you need to restart the service:

```bash
service knot restart
```

Check if the service is running:

```bash
service knot status
```
```
● knot.service - Knot DNS server
     Loaded: loaded (/usr/lib/systemd/system/knot.service; enabled; preset: enabled)
     Active: active (running) since Wed 2025-02-26 09:29:03 UTC; 4min 38s ago
       Docs: man:knotd(8)
             man:knot.conf(5)
             man:knotc(8)
    Process: 136276 ExecStartPre=/usr/sbin/knotc conf-check (code=exited, status=0/SUCCESS)
   Main PID: 136278 (knotd)
      Tasks: 17 (limit: 2276)
     Memory: 2.8M (peak: 3.1M)
        CPU: 44ms
     CGroup: /system.slice/knot.service
             └─136278 /usr/sbin/knotd -m 512

Feb 26 09:29:03 studentvirtual033 knotd[136278]: info: binding to interface ::1@53
Feb 26 09:29:03 studentvirtual033 knotd[136278]: info: binding to interface 2001:db8:abcd:1234:5678:9abc:def0:1234@53
Feb 26 09:29:03 studentvirtual033 knotd[136278]: info: loading 1 zones
Feb 26 09:29:03 studentvirtual033 knotd[136278]: info: [examdomain.com.] zone will be loaded
Feb 26 09:29:03 studentvirtual033 knotd[136278]: info: starting server
Feb 26 09:29:03 studentvirtual033 knotd[136278]: info: [examdomain.com.] zone file parsed, serial 1
Feb 26 09:29:03 studentvirtual033 knotd[136278]: info: [examdomain.com.] loaded, serial none -> 1, 1173 bytes
Feb 26 09:29:03 studentvirtual033 knotd[136278]: info: control, binding to '/run/knot/knot.sock'
Feb 26 09:29:03 studentvirtual033 knotd[136278]: info: server started in the foreground, PID 136278
Feb 26 09:29:03 studentvirtual033 systemd[1]: Started knot.service - Knot DNS server.
```

You can find more detailed configuration options in the official Knot DNS documentation at https://www.knot-dns.cz/docs/latest/html/index.html.

## Functionality Check
If not already done, to verify functionality, you need to configure the target IP address of the DNS server on a client device. This can be done by adding a line in the /etc/systemd/resolved.conf file with the DNS server's IP address, for example:

```
DNS=2001:db8:abcd:1234:5678:9abc:def0:1234
```

Then, restart the service:

```bash
sudo service systemd-resolved restart
```

I also tested the DNS request handling on the client device using the dig command with the domain parameter for device **vir34** and the AAAA parameter, which is used to query the IPv6 address:

```bash
dig vir34.examdomain.com AAAA
```

```
; <<>> DiG 9.18.30-0ubuntu0.24.04.2-Ubuntu <<>> vir34.examdomain.com AAAA
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 40233
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 65494
;; QUESTION SECTION:
;vir34.examdomain.com.              IN      AAAA

;; ANSWER SECTION:
vir34.examdomain.com.       3540    IN      AAAA    2001:db8:abcd:1234:5678:9abc:def0:abcd

;; Query time: 0 msec
;; SERVER: 127.0.0.53#53(127.0.0.53) (UDP)
;; WHEN: Wed Feb 26 09:34:55 UTC 2025
;; MSG SIZE  rcvd: 73
```

A successful response for the DNS query should have the ANSWER section, which contains the desired IPv6 address (in my case `2001:db8:abcd:1234:5678:9abc:def0:abcd`).

## References
[^cloudflare_ip]: *Cloudflare Docs: IP addresses* [online]. [cit. 2025-02-25]. Available from: https://developers.cloudflare.com/1.1.1.1/ip-addresses/
[^root]: *Root.cz: Deploying Knot DNS on your domain: a practical guide* [online]. [cit. 2025-02-25]. Available from: https://www.root.cz/clanky/nasazujeme-knot-dns-na-vlastni-domene-prakticky-navod/
