import arrow
import re
import requests
import gzip
import json
from prompt_toolkit.shortcuts import ProgressBar
from io import BytesIO
from nested_lookup import nested_lookup
from kittysploit.core.base.io import (
    print_success,
    print_status,
    print_error,
    print_warning,
    confirm,
)
from kittysploit.core.database.schema import db, Meta, Cve


class Update_cve:

    def __init__(self):
        self.current_year = arrow.now().year
        self.cve_first_year = 2002
        self.nvd_cve_url = (
            "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{year}.json.gz"
        )

    def check_for_update(self):
        """Check for cve update"""
        NVD_MODIFIED_META_URL = (
            "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-modified.meta"
        )

        print_success("Checking...")
        try:
            resp = requests.get(NVD_MODIFIED_META_URL)
        except Exception as e:
            print_error(e)
            return
        buf = BytesIO(resp.content).read().decode("utf-8")

        matches = re.match(r".*sha256:(\w{64}).*", buf, re.DOTALL)
        nvd_sha256 = matches.group(1)
        get_hash = db.query(Meta.value).first()
        if not get_hash:
            answer = self.confirm_download()
            if answer:
                self.download()

        elif nvd_sha256 != get_hash[0]:
            print_status("New version available")
            self.update()
        else:
            print_success("Cve up to date")

    def confirm_download(self):
        print_warning("This update can take several minutes")
        print_warning(
            "You need 140Mo of space disk space to download the full NVD feed"
        )
        answer = confirm("Download now? ")
        return answer

    def flatten_vendors(self, vendors):
        """Takes a list of nested vendors and products and flat them."""
        data = []
        for vendor, products in vendors.items():
            data.append(vendor)
            for product in products:
                data.append(f"{vendor}$PRODUCT${product}")
        return data

    def get_cwes(self, problems):
        """Takes a list of problems and return the CWEs ID."""
        return list(set([p["value"] for p in problems]))

    def convert_cpes(self, conf):
        """
        This function takes an object, extracts its CPE uris and transforms them into
        a dictionnary representing the vendors with their associated products.
        """
        uris = nested_lookup("cpe23Uri", conf) if not isinstance(conf, list) else conf

        # Create a list of tuple (vendor, product)
        cpes_t = list(set([tuple(uri.split(":")[3:5]) for uri in uris]))

        # Transform it into nested dictionnary
        cpes = {}
        for vendor, product in cpes_t:
            if vendor not in cpes:
                cpes[vendor] = []
            cpes[vendor].append(product)

        return cpes

    def download(self):
        """Download first the CVEs from 2002 to the current year"""
        NVD_MODIFIED_META_URL = (
            "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-modified.meta"
        )
        print_status(f"Get metadata sha256 {NVD_MODIFIED_META_URL}...")
        resp = requests.get(NVD_MODIFIED_META_URL)
        buf = BytesIO(resp.content).read().decode("utf-8")

        matches = re.match(r".*sha256:(\w{64}).*", buf, re.DOTALL)
        nvd_sha256 = matches.group(1)
        print_success("Done")
        add_meta = Meta("nvd", nvd_sha256)
        db.add(add_meta)
        db.commit()
        print_status("Download and extract cve ...")
        with ProgressBar() as pb:
            for year in pb(range(self.cve_first_year, self.current_year + 1)):

                # Download the file
                url = self.nvd_cve_url.format(year=year)
                resp = requests.get(url).content

                # Parse the XML elements
                raw = gzip.GzipFile(fileobj=BytesIO(resp)).read()
                items = json.loads(raw.decode("utf-8"))["CVE_Items"]
                for item in items:
                    cve = item["cve"]["CVE_data_meta"]["ID"]
                    if not cve:
                        cve = ""
                    summary = item["cve"]["description"]["description_data"][0]["value"]
                    cvss2 = (
                        item["impact"]["baseMetricV2"]["cvssV2"]["baseScore"]
                        if "baseMetricV2" in item["impact"]
                        else None
                    )
                    cvss3 = (
                        item["impact"]["baseMetricV3"]["cvssV3"]["baseScore"]
                        if "baseMetricV3" in item["impact"]
                        else None
                    )
                    cwes = self.get_cwes(
                        item["cve"]["problemtype"]["problemtype_data"][0]["description"]
                    )
                    cpes = self.convert_cpes(item["configurations"])
                    vendors = self.flatten_vendors(cpes)
                    create_at = (arrow.get(item["publishedDate"]).datetime,)
                    update_at = (arrow.get(item["lastModifiedDate"]).datetime,)
                    add_cve = Cve(
                        cve_id=cve,
                        summary=summary,
                        vendors=f"{vendors}",
                        cwes=f"{cwes}",
                        cvss2=f"{cvss2}",
                        cvss3=f"{cvss3}",
                        create_at=create_at[0],
                        update_at=update_at[0],
                    )
                    db.add(add_cve)
                    db.flush()
                db.commit()
        print_status("Done")

    def update(self):
        """Update the CVE database"""
        NVD_MODIFIED_URL = (
            "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-modified.json.gz"
        )
        print_success(f"Downloading {NVD_MODIFIED_URL}...")
        try:
            resp = requests.get(NVD_MODIFIED_URL).content
        except Exception as e:
            print_error(e)
            return
        raw = gzip.GzipFile(fileobj=BytesIO(resp)).read()
        items = json.loads(raw.decode("utf-8"))["CVE_Items"]
        print_status("Updating CVE database...")
        with ProgressBar() as pb:
            for count, item in pb(enumerate(items)):
                cve = item["cve"]["CVE_data_meta"]["ID"]
                if not cve:
                    cve = ""
                summary = item["cve"]["description"]["description_data"][0]["value"]
                cvss2 = (
                    item["impact"]["baseMetricV2"]["cvssV2"]["baseScore"]
                    if "baseMetricV2" in item["impact"]
                    else None
                )
                cvss3 = (
                    item["impact"]["baseMetricV3"]["cvssV3"]["baseScore"]
                    if "baseMetricV3" in item["impact"]
                    else None
                )
                cwes = self.get_cwes(
                    item["cve"]["problemtype"]["problemtype_data"][0]["description"]
                )
                cpes = self.convert_cpes(item["configurations"])
                vendors = self.flatten_vendors(cpes)
                create_at = (arrow.get(item["publishedDate"]).datetime,)
                update_at = (arrow.get(item["lastModifiedDate"]).datetime,)
                cve_obj = db.query(Cve).filter(Cve.cve_id == cve).first()
                try:
                    if not cve_obj:
                        add_cve = Cve(
                            cve_id=cve,
                            summary=summary,
                            vendors=f"{vendors}",
                            cwes=f"{cwes}",
                            cvss2=f"{cvss2}",
                            cvss3=f"{cvss3}",
                            create_at=create_at[0],
                            update_at=update_at[0],
                        )
                        db.add(add_cve)
                        db.flush()
                    else:
                        cve_obj.summary = summary
                        cve_obj.vendors = f"{vendors}"
                        cve_obj.cwes = f"{cwes}"
                        cve_obj.cvss2 = f"{cvss2}"
                        cve_obj.cvss3 = f"{cvss3}"
                        cve_obj.create_at = create_at[0]
                        cve_obj.update_at = update_at[0]
                        db.flush()
                except:
                    continue
            db.commit()
        print_status("Done")
