from django.contrib import admin
from .models import *


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    readonly_fields = [
        'sender',
        'sender_title',
        'recipient',
        'subject',
        'build_body',
        'delivered',
    ]

    list_display = [
        'recipient',
        'subject',
        'delivered',
        'created_at',
        'updated_at',
    ]

    exclude = ['body']

    search_fields = [
        'recipient'
    ]

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False

    def build_body(self, obj):
        src_no_double_quotes = obj.body.replace('"', "'")
        split_on_newlines = src_no_double_quotes.split('\n')
        write_hack = ''.join(['win.document.write("{}\\n");'.format(s) for s in split_on_newlines])
        # __import__('ipdb').set_trace()
        return """
        <iframe id="body-frame" srcdoc="{src}" style="display: none;width:100%;height:400px; "></iframe>
        <a id="toggle" href="javascript:toggleFrame()">Show body in inline frame</a>
        <br />
        <br />
        <a href="javascript:launchPreview()">Launch preview in new window</a>
        <script>
        var frame = document.getElementById('body-frame');
        var toggle = document.getElementById('toggle');
        var hidden = true;

        function toggleFrame() {{
            if (hidden) {{
                frame.style.display = 'block';
                toggle.innerHTML = 'Hide inline frame';
            }} else {{
                frame.style.display = 'none';
                toggle.innerHTML = 'Show body in inline frame';
            }}
            hidden = !hidden;
        }}

        function launchPreview() {{
            var win = window.open("", "win", "width=300,height=200");
            win.document.open("text/html", "replace");
            {write_hack}
            win.document.close();

        }}
        </script>
        """.format(src=src_no_double_quotes, write_hack=write_hack)

    build_body.allow_tags = True
    build_body.short_description = 'Body'

@admin.register(MailEvent)
class MailEventAdmin(admin.ModelAdmin):
    list_display = [
        'recipient',
        'type',
        'timestamp',
    ]

    search_fields = [
        'recipient'
    ]

    list_filter = [
        'type'
    ]

    readonly_fields = [
        'recipient',
        'type',
        'timestamp', 
        'url'
    ]

    def has_add_permission(*args, **kwargs):
        return False

    def has_delete_permission(*args, **kwargs):
        return False