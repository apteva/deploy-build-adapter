"""Development-only generator; shared stages come from the maintained native workflow."""
import json
import re
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def stages():
    source = yaml.safe_load((ROOT / 'codemagic.yaml').read_text())
    steps = source['workflows']['apteva-mobile-capsule']['scripts']
    result = []
    for step in steps:
        script = step['script'].replace('CM_BUILD_DIR', 'APTEVA_BUILD_DIR').replace('CM_ENV', 'APTEVA_ENV_FILE')
        script = re.sub(r'(?m)^( +)app-store-connect fetch-signing-files[^\n]+\n +keychain add-certificates\n +xcode-project use-profiles',
            lambda m: m[1] + 'python3 "$APTEVA_BUILD_DIR/scripts/install_managed_signing.py"\n' + m[1] + 'xcode-project use-profiles --profile "$APTEVA_BUILD_DIR/apteva-signing/profile.mobileprovision"', script)
        script = script.replace('zip -qry "$APTEVA_BUILD_DIR/apteva-build.zip" .',
            'zip -qry "$APTEVA_BUILD_DIR/${APTEVA_ARTIFACT_NAME:-apteva-build}.zip" .')
        result.append({'name': step['name'], 'script': script})
    return result


if __name__ == '__main__':
    (ROOT / 'scripts' / 'mobile_steps.json').write_text(json.dumps(stages(), indent=2) + '\n')
