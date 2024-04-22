

# Eidgenoessische Abstimmungen
url = base_absitmmung_url()['Eidgenössisch']
url_list = make_url_list(url, headers, SSL_VERIFY)



# Kantonale Abstimmungen
url = base_absitmmung_url()['Kanton Zürich']
url_list = make_url_list(url, headers, SSL_VERIFY)


# Kommunale Abstimmungen
url = base_absitmmung_url()['Stadt Zürich']
url_list = make_url_list(url, headers, SSL_VERIFY)
