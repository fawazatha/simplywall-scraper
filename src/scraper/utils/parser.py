import json
import re


def sanitize_js_object_literal(raw_js: str) -> str:
    sanitized = re.sub(r':\s*undefined\b', ': null', raw_js)
    sanitized = re.sub(r',\s*undefined\b', ', null', sanitized)
    sanitized = re.sub(r'\bundefined\s*,', 'null,', sanitized)
    sanitized = re.sub(r'new Map\(\[.*?\]\)', 'null', sanitized, flags=re.DOTALL)
    return sanitized


def extract_react_query_state(html_content: str) -> dict:
    marker = '__REACT_QUERY_STATE__'
    marker_index = html_content.find(marker)

    if marker_index == -1:
        raise ValueError(f"{marker} not found in page HTML")

    json_start = html_content.index('{', marker_index)
    json_end = html_content.find('</script>', json_start)
    raw_js = html_content[json_start:json_end]

    return json.loads(sanitize_js_object_literal(raw_js))


def extract_redux_state(html_content: str) -> dict:
    marker = 'window.REDUX_STATE'
    marker_index = html_content.find(marker)

    if marker_index == -1:
        raise ValueError(f"{marker} not found in page HTML")

    json_start = html_content.index('{', marker_index)
    json_end = html_content.find('</script>', json_start)
    raw_js = html_content[json_start:json_end].rstrip().rstrip(';')

    return json.loads(sanitize_js_object_literal(raw_js))


def extract_management_and_ownership(html_content: str) -> dict:
    react_query_data = extract_react_query_state(html_content)

    raw_data = (
        react_query_data['queries'][0]['state']['data']
        ['data']['analysis']['data']['extended']
        ['data']['raw_data']['data']
    )

    redux_data = extract_redux_state(html_content)
    top_shareholders_by_company = redux_data['company']['topShareholders']

    if len(top_shareholders_by_company) != 1:
        raise ValueError(
            f"Expected exactly 1 company key in topShareholders, "
            f"got {len(top_shareholders_by_company)}"
        )

    company_uuid = next(iter(top_shareholders_by_company))
    shareholder_entries = top_shareholders_by_company[company_uuid]

    top_shareholders = sorted(
        shareholder_entries.values(),
        key=lambda entry: entry['rankSharesHeld']
    )

    return {
        'management': raw_data['members'],
        'ownership_by_type': raw_data['ownership'],
        'top_shareholders': top_shareholders,
    }
