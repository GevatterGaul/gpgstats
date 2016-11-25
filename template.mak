## -*- coding: utf-8 -*-
<%
    from urllib.parse import quote
%>

<%def name="keyserver_link(email, text=None)">
    % if email is not None:
        <a href="http://keyserver.int.catech.com:11371/pks/lookup?op=vindex&search=+${quote(email)}&fingerprint=on">${text or email}</a>
    % else:
        ${text or email}
    % endif
</%def>

<%def name="mail_link(email)">
    % if email is not None:
        <a href="mailto:${email}">${email}</a>
    % endif
</%def>

<!DOCTYPE html>
<html>
	<head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <meta http-equiv="x-ua-compatible" content="ie=edge">

		<title>TNG GnuPG Statistics</title>

		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.3/css/bootstrap.min.css" integrity="sha384-MIwDKRSSImVFAZCVLtU0LMDdON6KVCrZHyVQQj6e8wIEJkW4tvwqXrbMIya1vriY" crossorigin="anonymous">

		<link
		    href="http://cdn.pydata.org/bokeh/release/bokeh-0.12.1.min.css"
		    rel="stylesheet" type="text/css">
		<link
		    href="http://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.1.min.css"
		    rel="stylesheet" type="text/css">

		<script src="http://cdn.pydata.org/bokeh/release/bokeh-0.12.2.min.js"></script>
		<script src="http://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.2.min.js"></script>
	</head>
	<body>
        <h3>Total Signatures</h3>
        ${total_keys_and_sigs_div}
        ${total_keys_and_sigs_script}

        % if show_ca_info:
            <h3>TNG Auto Signing Key</h3>
            <div class="container-fluid">
                <div class="row">
                    <div class="col-md-4">
                        <h4>
                            Total Signatures
                        </h4>
                        ${total_ca_auto_signatures}
                    </div>
                    <div class="col-md-4">
                        <h4>
                            &#37; Of Total Signatures
                        </h4>
                        ${percent_of_total_ca_signatures}
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-4">
                        <h4>
                            Signs this Month
                        </h4>
                        ${total_ca_auto_signatures_this_month}
                    </div>
                    <div class="col-md-4">
                        <h4>
                            &#37; of Signs this Month
                        </h4>
                        ${percent_of_total_signatures_this_month}
                    </div>
                </div>
            </div>
        % endif

        <h3>Signs Per Month</h3>
		${signs_per_month_div}
		${signs_per_month_script}

        <h3>Top Contributors</h3>
        <table class="table table-striped">
            <thead>
            <tr>
                <th>#</th>
                <th>Signatures</th>
                <th>Key</th>
                <th>Name</th>
                <th>Email</th>
            </tr>
            </thead>
            <tbody>
                % for num, contributor in enumerate(top_contributors):
                    <tr>
                        <th scope="row">${num+1}</th>
                        <td>${contributor.num_sigs}</td>
                        <td>${keyserver_link(contributor.email, contributor.key)}</td>
                        <td>${contributor.name or ''}</td>
                        <td>${mail_link(contributor.email)}</td>
                    </tr>
                % endfor
            </tbody>
        </table>

    <h3>Top Monthly Contributors</h3>
    <table class="table table-striped">
        <thead>
        <tr>
            <th>Date</th>
            <th>Signatures</th>
            <th>Key</th>
            <th>Name</th>
            <th>Email</th>
        </tr>
        </thead>
        <tbody>
            % for contributor in top_contributors_by_month:
                <tr>
                    <th scope="row">${contributor.sign_month}</th>
                    <td>${contributor.num_sigs}</td>
                    <td>${keyserver_link(contributor.email, contributor.key)}</td>
                    <td>${contributor.name or ''}</td>
                    <td>${mail_link(contributor.email)}</td>
                </tr>
            % endfor
        </tbody>
    </table>

    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.0.0/jquery.min.js" integrity="sha384-THPy051/pYDQGanwU6poAc/hOdQxjnOEXzbT+OuUAFqNqFjL+4IGLBgCJC3ZOShY" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tether/1.2.0/js/tether.min.js" integrity="sha384-Plbmg8JY28KFelvJVai01l8WyZzrYWG825m+cZ0eDDS1f7d/js6ikvy1+X+guPIB" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.4/js/bootstrap.min.js" integrity="sha384-VjEeINv9OSwtWFLAtmc4JCtEJXXBub00gtSnszmspDLCtC0I4z4nqz7rEFbIZLLU" crossorigin="anonymous"></script>
	</body>
</html>
