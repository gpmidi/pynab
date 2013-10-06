<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nzb PUBLIC "-//newzBin//DTD NZB 1.1//EN" "http://www.newzbin.com/DTD/nzb/nzb-1.1.dtd">
    <%!
        import pytz
        from pynab.nzb import NZB
    %>
<nzb xmlns="http://www.newzbin.com/DTD/2003/nzb">
    <head>
        % if category:
            <meta type="category">${category['name'] | x}</meta>
        % endif
        <meta type="name">${name | x}</meta>
    </head>

    % for pkey, part in sorted(binary['parts'].items()):
    <%
        timestamp = '{:.0f}'.format(part['posted'].replace(tzinfo=pytz.utc).timestamp())
        subject = '{0} (1/{1:d})'.format(part['subject'], part['total_segments'])
    %>
        <file poster="${part['posted_by'] | x}" date="${timestamp | x}" subject="${subject | x}">
            <groups>
                % for group in NZB.parse_xref(binary['xref']):
                    <group>${group}</group>
                % endfor
            </groups>

            <segments>
                % for skey, segment in sorted(part['segments'].items()):
                <%
                    uskey = '{:d}'.format(int(skey))
                %>
                    <segment bytes="${segment['size']}" number="${uskey}">${segment['message_id']}</segment>
                % endfor
            </segments>
        </file>
    % endfor
    <!-- generated by pynab ${version} -->
</nzb>