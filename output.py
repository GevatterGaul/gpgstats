# -*- coding: utf-8 -*-

import pandas
from dateutils import relativedelta
from datetime import date
from sqlalchemy import func, desc, asc
from mako.template import Template
from bokeh.charts import Bar, TimeSeries
from bokeh.embed import components

from models import Key, Signature

class HTMLOutput():
    def __init__(self, session, ca_key, domain):
        self.session = session
        self.ca_key = ca_key
        self.domain = domain

    def domain_query(self, *args):
        if self.domain is not None:
            return self.session.query(*args).filter(Key.email.like('%{}'.format(self.domain)))
        else:
            return self.session.query(*args)

    @property
    def total_sigs(self):
        return self.session.query(Signature).count()

    @property
    def total_sigs_this_month(self):
        return self.session.query(Signature).filter(Signature.sign_date >= date.today().replace(day=1)).count()

    @property
    def total_ca_auto_sigs(self):
        return self.session.query(Signature).filter(Signature.signer_key == self.ca_key).count()

    @property
    def total_ca_auto_sigs_this_month(self):
        return self.session.query(Signature).filter(
            Signature.signer_key == self.ca_key,
            Signature.sign_date >= date.today().replace(day=1)
        ).count()

    @property
    def total_keys_and_sigs(self):
        sigs = self.domain_query(
            func.COUNT(Signature.id).label('num_sigs'),
            Signature.sign_date
        ).join(Key).filter(
            Signature.sign_date > date.today()-relativedelta(years=2)
        ).group_by(Signature.sign_date).order_by(asc(Signature.sign_date)).all()

        current_num_sigs = self.session.query(Signature).filter(Signature.sign_date <= date.today()-relativedelta(years=2)).count()

        if self.ca_key is not None:
            ca_sigs = self.domain_query(
                func.COUNT(Signature.id).label('num_sigs'),
                Signature.sign_date
            ).join(Key).filter(
                Signature.sign_date > date.today()-relativedelta(years=2),
                Signature.signer_key == self.ca_key
            ).group_by(Signature.sign_date).order_by(asc(Signature.sign_date)).all()

            current_num_ca_sigs = self.session.query(Signature).filter(
                Signature.sign_date <= date.today()-relativedelta(years=2), Signature.signer_key == self.ca_key).count()
        else:
            ca_sigs = []
            current_num_ca_sigs = 0

        keys = self.domain_query(
            func.COUNT(Key.id).label('num_keys'),
            Key.created
        ).filter(
            Key.created > date.today()-relativedelta(years=2)
        ).group_by(Key.created).order_by(asc(Key.created)).all()

        current_num_keys = self.session.query(Key).filter(Key.created <= date.today()-relativedelta(years=2)).count()

        sig_dates = [pandas.Timestamp(sig.sign_date) for sig in sigs]
        ca_sig_dates = [pandas.Timestamp(sig.sign_date) for sig in ca_sigs]
        key_dates = [pandas.Timestamp(key.created) for key in keys]

        dates = list(set(sig_dates + key_dates + ca_sig_dates))
        dates.sort()
        date_num_sigs = []
        date_num_ca_sigs = []
        date_num_keys = []

        for d in dates:
            try:
                i = sig_dates.index(d)
                current_num_sigs = current_num_sigs + sigs[i].num_sigs
            except:
                pass
            finally:
                date_num_sigs.append(current_num_sigs)

            try:
                i = ca_sig_dates.index(d)
                current_num_ca_sigs = current_num_ca_sigs + ca_sigs[i].num_sigs
            except:
                pass
            finally:
                date_num_ca_sigs.append(current_num_ca_sigs)

            try:
                i = key_dates.index(d)
                current_num_keys = current_num_keys + keys[i].num_keys
            except:
                pass
            finally:
                date_num_keys.append(current_num_keys)

        data = {
            'Signatures': date_num_sigs,
            'Keys': date_num_keys,
            'Dates': pandas.Series(dates)
        }

        y_labels = ['Signatures', 'Keys']

        if self.ca_key is not None:
            data['CA Auto Signatures'] = date_num_ca_sigs
            y_labels.append('CA Auto Signatures')

        t = TimeSeries(data, x='Dates', y=y_labels, plot_width=800)

        return components(t)

    @property
    def signs_per_month_plot(self):
        signs_per_month_data = self.domain_query(
            func.strftime('%Y-%m', Signature.sign_date).label('sign_month'),
            func.COUNT(Signature.id).label('num_sigs')
        ).join(Key).filter(
            Signature.sign_date>date.today()-relativedelta(years=2)
        ).group_by('sign_month').order_by(asc('sign_month')).all()

        data = dict(
            signs=[sig.num_sigs for sig in signs_per_month_data],
            months=[sig.sign_month for sig in signs_per_month_data]
        )

        b = Bar(data, values='signs', label='months', plot_width=800, legend=False, color='#0275d8')

        return components(b)

    @property
    def top_contributors_by_month(self):
        grouped_sigs = self.session.query(
            Signature.signer_key.label('key'),
            Signature.signer_name.label('name'),
            Signature.signer_email.label('email'),
            func.strftime('%Y-%m', Signature.sign_date).label('sign_month'),
            func.COUNT(Signature.id).label('num_sigs')
        ).join(Key).filter(Signature.signer_key != self.ca_key).group_by('key', 'sign_month').subquery()

        return self.session.query(
            grouped_sigs.c.key,
            grouped_sigs.c.name,
            grouped_sigs.c.email,
            grouped_sigs.c.sign_month,
            grouped_sigs.c.num_sigs
        ).group_by(grouped_sigs.c.sign_month).having(grouped_sigs.c.num_sigs==func.MAX(grouped_sigs.c.num_sigs)).\
        order_by(desc(grouped_sigs.c.sign_month)).limit(24).all()

    @property
    def top_contributors(self):
        return self.session.query(
            Signature.signer_key.label('key'),
            Signature.signer_name.label('name'),
            Signature.signer_email.label('email'),
            func.COUNT(Signature.signer_key).label('num_sigs')
        ).filter(Signature.signer_key != self.ca_key).\
        group_by(Signature.signer_key).order_by(desc('num_sigs')).limit(10).all()

    def gen_html(self):
        signs_per_month_script, signs_per_month_div = self.signs_per_month_plot
        total_keys_and_sigs_script, total_keys_and_sigs_div = self.total_keys_and_sigs

        template = Template(filename='template.mak')
        out = open('stats.html', 'w')

        template_args = dict(
            signs_per_month_div=signs_per_month_div,
            signs_per_month_script=signs_per_month_script,
            total_keys_and_sigs_div=total_keys_and_sigs_div,
            total_keys_and_sigs_script=total_keys_and_sigs_script,
            top_contributors=self.top_contributors,
            top_contributors_by_month=self.top_contributors_by_month,
        )

        if self.ca_key is not None:
            template_args.update(dict(
                show_ca_info=True,
                total_ca_auto_signatures=self.total_ca_auto_sigs,
                total_ca_auto_signatures_this_month=self.total_ca_auto_sigs_this_month,
                percent_of_total_ca_signatures=self.total_ca_auto_sigs/self.total_sigs,
                percent_of_total_signatures_this_month=self.total_ca_auto_sigs_this_month/self.total_sigs_this_month
            ))
        else:
            template_args.update(dict(
                show_ca_info=False
            ))

        out.write(template.render(**template_args))
        out.close()
