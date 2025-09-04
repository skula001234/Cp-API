import requests
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
from bs4 import BeautifulSoup
import os
import glob
import logging

logger = logging.getLogger(__name__)

def get_video_info(url, headers):
    try:
        api_url = f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}'
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except Exception as e:
        return {"success": False, "error": f"API request failed: {e}"}

def get_mpd_content(mpd_url):
    try:
        response = requests.get(mpd_url, timeout=15)
        response.raise_for_status()
        return {"success": True, "data": response.text}
    except Exception as e:
        return {"success": False, "error": f"MPD download failed: {e}"}

def extract_pssh_from_mpd(mpd_content):
    try:
        soup = BeautifulSoup(mpd_content, 'lxml-xml')
        pssh_element = soup.find('cenc:pssh')
        if pssh_element and pssh_element.string:
            return {"success": True, "data": pssh_element.string.strip()}
        return {"success": False, "error": "Widevine PSSH not found in MPD."}
    except Exception as e:
        return {"success": False, "error": f"PSSH extraction error: {e}"}

def get_decryption_keys_from_license(pssh, license_url, headers):
    session_id = None
    try:
        wvd_dir = os.path.join(os.getcwd(), 'WVDs')
        wvd_files = glob.glob(os.path.join(wvd_dir, '*.wvd'))
        if not wvd_files:
            return {"success": False, "error": "No .wvd file found in WVDs directory. This file is required for DRM."}
        
        device = Device.load(wvd_files[0])
        cdm = Cdm.from_device(device)
        session_id = cdm.open()
        
        challenge = cdm.get_license_challenge(session_id, PSSH(pssh))
        
        license_headers = headers.copy()
        license_headers.update({"Content-Type": "application/octet-stream"})
        
        license_response = requests.post(license_url, data=challenge, headers=license_headers, timeout=20)
        license_response.raise_for_status()

        cdm.parse_license(session_id, license_response.content)
        
        keys = [f"--key {key.kid.hex()}:{key.key.hex()}" for key in cdm.get_keys(session_id) if key.type != "SIGNING"]
        if not keys:
            return {"success": False, "error": "No decryption keys found in license."}

        return {"success": True, "data": keys}
    finally:
        if session_id: cdm.close(session_id)

def extract_keys_from_url(video_url, token):
    headers = {"x-access-token": token}
    
    video_info_res = get_video_info(video_url, headers)
    if not video_info_res["success"]: return video_info_res
    
    video_data = video_info_res["data"]
    if video_data.get("status") != "ok":
        return {"success": False, "error": f"API Error: {video_data.get('message', 'Could not get video info')}"}

    mpd_url = video_data["drmUrls"]["manifestUrl"]
    license_url = video_data["drmUrls"]["licenseUrl"]
    
    mpd_content_res = get_mpd_content(mpd_url)
    if not mpd_content_res["success"]: return mpd_content_res
    
    pssh_res = extract_pssh_from_mpd(mpd_content_res["data"])
    if not pssh_res["success"]: return pssh_res
    
    keys_res = get_decryption_keys_from_license(pssh_res["data"], license_url, headers)
    if keys_res["success"]:
        keys_res["mpd_url"] = mpd_url
    
    return keys_res
