"""Attach supplemental visual archives without rewriting source metadata."""

import struct
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.models import Asset, AssetRelation, BenchmarkCreative, ExampleLink, RegressionTest
from creative_os.util import sha256_bytes, utcnow
from creative_os.validation.checks import aspect_ratio_status

SUPPLEMENT_NOTE = "Supplemental bytes stored beside the core snapshot. Core snapshot bytes were not changed."
UNRESOLVED_RELATIONSHIPS = [
    "Target S3 final has no recorded base, ingredient, or reference parent.",
    "The AirPods 5 screenshot is the S2 base. A crop from the order-details plate is not stated.",
    "Rejected v1 slide 1 has no recorded base. QA names a builder, not the keyboard PNG.",
    "Rejected v1 slide 3 has no recorded base.",
    "Brooke sequel and Dasher-got-nosy have no binary in the supplemental archives.",
    "DoorDash bases, golden-example files, and the viral corpus have no supplemental binaries.",
]


def import_visual_supplements(session: Session, supplement_root: Path) -> dict[str, int]:
    if not supplement_root.is_dir():
        raise FileNotFoundError(f"supplement root is missing: {supplement_root}")
    counts = {
        "files_seen": 0,
        "index_matches": 0,
        "archive_a_files": 0,
        "archive_b_files": 0,
        "child_assets": 0,
        "hashes": 0,
        "relations": 0,
        "example_links": 0,
        "skipped": 0,
    }
    index = _file_index(session)
    ingredients = _named(session, "S2 product images")
    rejected = _named(session, "Target v1 rejected")
    for path in sorted(supplement_root.rglob("*")):
        if not path.is_file() or path.name == "CURSOR_SPLIT_README.md":
            continue
        counts["files_seen"] += 1
        relative = path.relative_to(supplement_root).as_posix()
        if relative.startswith("examples/target_chore_stuff_v6/"):
            counts["archive_a_files"] += 1
        elif relative.startswith("examples/failures_v1_rejected/"):
            counts["archive_b_files"] += 1
        data = path.read_bytes()
        digest = sha256_bytes(data)
        width, height = _image_size(data)
        mime = _mime(path)
        matched = index.get(path.name, [])
        if len(matched) == 1:
            _fill_existing(matched[0], relative, digest, len(data), mime, width, height)
            counts["index_matches"] += 1
            counts["hashes"] += 1
            asset = matched[0]
        else:
            child, created = _child_asset(
                session,
                relative,
                digest,
                len(data),
                mime,
                width,
                height,
                ingredients,
                rejected,
            )
            if child is None:
                counts["skipped"] += 1
                continue
            asset = child
            if created:
                counts["child_assets"] += 1
            counts["hashes"] += 1
        if "ingredients/" in relative and ingredients is not None:
            note = "Member of the indexed S2 ingredients directory."
            if _relate(session, asset, ingredients, "MEMBER_OF", note):
                counts["relations"] += 1
        if relative.startswith("examples/failures_v1_rejected/") and rejected is not None:
            note = "Member of the indexed stale Target v1 directory."
            if _relate(session, asset, rejected, "MEMBER_OF", note):
                counts["relations"] += 1
    counts["relations"] += _target_relations(session)
    counts["example_links"] += _example_links(session)
    return counts


def _file_index(session: Session) -> dict[str, list[Asset]]:
    grouped: dict[str, list[Asset]] = {}
    for asset in session.scalars(select(Asset)).all():
        if asset.original_path.endswith("/"):
            continue
        grouped.setdefault(Path(asset.original_path).name, []).append(asset)
    return grouped


def _named(session: Session, name: str) -> Asset | None:
    return session.scalar(select(Asset).where(Asset.name == name))


def _fill_existing(
    asset: Asset,
    relative: str,
    digest: str,
    size: int,
    mime: str,
    width: int | None,
    height: int | None,
) -> None:
    asset.content_hash = digest
    asset.size_bytes = size
    asset.mime_type = mime
    asset.width = width
    asset.height = height
    asset.present_in_snapshot = True
    asset.storage_uri = f"source_snapshots/supplements/2026-10-05/{relative}"
    notes = (asset.notes or "").replace(" Binary is not in the core snapshot.", "").strip()
    if SUPPLEMENT_NOTE not in notes:
        asset.notes = f"{notes} {SUPPLEMENT_NOTE}".strip()


def _child_asset(
    session: Session,
    relative: str,
    digest: str,
    size: int,
    mime: str,
    width: int | None,
    height: int | None,
    ingredients: Asset | None,
    rejected: Asset | None,
) -> tuple[Asset | None, bool]:
    original = f"supplement://{relative}"
    existing = session.scalar(select(Asset).where(Asset.original_path == original))
    if existing:
        _fill_existing(existing, relative, digest, size, mime, width, height)
        return existing, False
    if "ingredients/" in relative:
        parent = ingredients
    elif "failures_v1_rejected/" in relative:
        parent = rejected
    else:
        parent = None
    if parent is None:
        return None, False
    name = Path(relative).name
    stale = bool(parent.stale)
    role = parent.role
    product_model = None
    if name == "3_airpods4.jpg":
        stale = True
        product_model = "AirPods 4"
        role = "INGREDIENT"
    elif relative.endswith(".md"):
        role = "REFERENCE"
    creative_id = parent.creative_id
    story_key = parent.story_key
    asset = Asset(
        creative_id=creative_id,
        reference_bank_id=None,
        bound_story_lock_version_id=None,
        name=name,
        role=role,
        rights_status="UNKNOWN",
        original_path=original,
        storage_uri=f"source_snapshots/supplements/2026-10-05/{relative}",
        content_hash=digest,
        size_bytes=size,
        mime_type=mime,
        width=width,
        height=height,
        present_in_snapshot=True,
        source_exists_claim=True,
        approved=None,
        stale=stale,
        ecosystem_code=parent.ecosystem_code,
        story_key=story_key,
        product_model=product_model,
        notes=(
            "No separate ASSET_INDEX file row. "
            f"Inherited role {role} and stale={stale} from {parent.name}. {SUPPLEMENT_NOTE}"
        ),
        created_at=utcnow(),
    )
    session.add(asset)
    session.flush()
    return asset, True


def _target_relations(session: Session) -> int:
    created = 0
    finals = {name: _named(session, name) for name in ("Target S1 final", "Target S2 final", "Target S3 final")}
    keyboard = _named(session, "iOS26 Messages keyboard base (user's own)")
    user_base = _named(session, "Tyrel's AirPods 5 Target screenshot")
    order_base = _named(session, "Target order details base")
    box = _named(session, "AirPods 5 box photo")
    stale_doc = _named(session, "Stale asset list")
    if finals["Target S1 final"] and keyboard:
        created += _relate(
            session,
            finals["Target S1 final"],
            keyboard,
            "BASE",
            "Index names this PNG the Messages keyboard base. It is in the v6 package beside s1_v6b.png.",
        )
    if finals["Target S2 final"] and user_base:
        created += _relate(
            session,
            finals["Target S2 final"],
            user_base,
            "BASE",
            "STALE_ASSETS.md says s2_user_airpods5.png is the base for s2_v6.",
        )
    if finals["Target S2 final"] and stale_doc:
        created += _relate(
            session,
            finals["Target S2 final"],
            stale_doc,
            "EVIDENCE",
            "STALE_ASSETS.md records the v6 finals and the stale date still printed on the user screenshot.",
        )
    if finals["Target S2 final"]:
        for name in (
            "1_candles_spiral.jpg",
            "2_funfetti.png",
            "4_streamers.png",
            "5_bounty.png",
        ):
            ingredient = _named(session, name)
            if ingredient:
                created += _relate(
                    session,
                    finals["Target S2 final"],
                    ingredient,
                    "INGREDIENT",
                    "File is in the v6 ingredients folder and is not the superseded AirPods 4 photo.",
                )
        if box:
            created += _relate(
                session,
                finals["Target S2 final"],
                box,
                "INGREDIENT",
                "v6 ingredients include airpods5_box_front.jpg, the indexed packaging photo.",
            )
    slide2 = _named(session, "slide2_target_order_details.png")
    if slide2 and order_base:
        created += _relate(
            session,
            slide2,
            order_base,
            "BASE",
            "PROVENANCE.md names 16_ORDER_DETAILS_darkmode_ready_for_pickup.jpeg as the slide 2 chrome.",
        )
    return created


def _example_links(session: Session) -> int:
    created = 0
    holdout = session.scalar(
        select(BenchmarkCreative).where(BenchmarkCreative.name == "SHE SAID IT WAS CHORE STUFF")
    )
    tests = {row.code: row for row in session.scalars(select(RegressionTest)).all()}
    for name, role, reason in (
        (
            "Target S1 final",
            "HOLDOUT",
            "Current produced S1 for the unposted Target holdout. Not a performance winner.",
        ),
        (
            "Target S2 final",
            "HOLDOUT",
            "Current produced S2 for the unposted Target holdout. Not a performance winner.",
        ),
        (
            "Target S3 final",
            "HOLDOUT",
            "Current produced S3 for the unposted Target holdout. Not a performance winner.",
        ),
        (
            "slide1_imessage.png",
            "STALE",
            "Indexed Target v1 rejected attempt. QA passed an older Drive Up dialogue.",
        ),
        (
            "slide2_target_order_details.png",
            "STALE",
            "Indexed Target v1 rejected attempt. Provenance records the superseded $5.33 basket.",
        ),
        (
            "slide3_birthday_camera_roll.png",
            "STALE",
            "Rejected v1 attempt. QA records 1080×1920, outside the program ratio.",
        ),
        (
            "QA_CAROUSEL.md",
            "REFERENCE",
            "QA notes for the rejected v1 attempt. Not a performance example.",
        ),
        (
            "PROVENANCE.md",
            "REFERENCE",
            "Provenance notes for the rejected v1 slide 2. Not a performance example.",
        ),
    ):
        created += _link_asset(session, name, role, reason, benchmark=holdout, regression=None)
    created += _link_asset(
        session,
        "3_airpods4.jpg",
        "STALE",
        "Filename and product are AirPods 4. The current lock is AirPods 5. Not linked as an S2 ingredient.",
        benchmark=None,
        regression=tests.get("T06"),
    )
    created += _link_asset(
        session,
        "AirPods 5 box photo",
        "GOOD",
        "Indexed packaging photo for the current AirPods 5 lock. Rights remain UNKNOWN.",
        benchmark=None,
        regression=tests.get("T06"),
    )
    created += _link_asset(
        session,
        "Target S2 final",
        "GOOD",
        "Current S2 final belongs to the AirPods 5 lock.",
        benchmark=None,
        regression=tests.get("T06"),
    )
    created += _link_asset(
        session,
        "Tyrel's AirPods 5 Target screenshot",
        "STALE",
        "STALE_ASSETS.md says this base still shows status bar 4:31 and pickup Wed, Oct 23.",
        benchmark=None,
        regression=tests.get("T05"),
    )
    for name in ("Target S1 final", "Target S2 final", "Target S3 final"):
        asset = _named(session, name)
        ratio_ok = (
            asset is not None
            and asset.width
            and asset.height
            and aspect_ratio_status(asset.width, asset.height)[0] == "PASS"
        )
        if ratio_ok and asset is not None:
            created += _link_asset(
                session,
                name,
                "GOOD",
                f"Measured {asset.width}×{asset.height} is inside the current program ratio tolerance.",
                benchmark=None,
                regression=tests.get("T14"),
            )
    slide3 = _named(session, "slide3_birthday_camera_roll.png")
    ratio_failed = (
        slide3 is not None
        and slide3.width
        and slide3.height
        and aspect_ratio_status(slide3.width, slide3.height)[0] == "FAIL"
    )
    if ratio_failed and slide3 is not None:
        created += _link_asset(
            session,
            slide3.name,
            "STALE",
            f"Measured {slide3.width}×{slide3.height} fails the program ratio. It stays stale.",
            benchmark=None,
            regression=tests.get("T14"),
        )
    return created


def _link_asset(
    session: Session,
    name: str,
    role: str,
    reason: str,
    benchmark: BenchmarkCreative | None,
    regression: RegressionTest | None,
) -> int:
    asset = _named(session, name)
    if asset is None or (benchmark is None and regression is None):
        return 0
    existing = session.scalar(
        select(ExampleLink).where(
            ExampleLink.asset_id == asset.id,
            ExampleLink.example_role == role,
            ExampleLink.benchmark_id == (benchmark.id if benchmark else None),
            ExampleLink.regression_test_id == (regression.id if regression else None),
        )
    )
    if existing:
        return 0
    session.add(
        ExampleLink(
            benchmark_id=benchmark.id if benchmark else None,
            regression_test_id=regression.id if regression else None,
            asset_id=asset.id,
            example_role=role,
            reason=reason,
            created_at=utcnow(),
        )
    )
    return 1


def _relate(session: Session, asset: Asset, related: Asset, relation: str, notes: str) -> int:
    if asset.id == related.id:
        return 0
    existing = session.scalar(
        select(AssetRelation).where(
            AssetRelation.asset_id == asset.id,
            AssetRelation.related_asset_id == related.id,
            AssetRelation.relation == relation,
        )
    )
    if existing:
        return 0
    session.add(AssetRelation(asset_id=asset.id, related_asset_id=related.id, relation=relation, notes=notes))
    return 1


def _mime(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "image/png"
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".md":
        return "text/markdown"
    return "application/octet-stream"


def _image_size(data: bytes) -> tuple[int | None, int | None]:
    if data.startswith(b"\x89PNG\r\n\x1a\n") and data[12:16] == b"IHDR":
        width, height = struct.unpack(">II", data[16:24])
        return width, height
    if data[:2] == b"\xff\xd8":
        return _jpeg_size(data)
    return None, None


def _jpeg_size(data: bytes) -> tuple[int | None, int | None]:
    index = 2
    while index < len(data) - 8:
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        if marker in {0xC0, 0xC1, 0xC2}:
            height, width = struct.unpack(">HH", data[index + 5 : index + 9])
            return width, height
        if marker in {0xD8, 0xD9}:
            index += 2
            continue
        if index + 4 > len(data):
            break
        segment = struct.unpack(">H", data[index + 2 : index + 4])[0]
        index += 2 + segment
    return None, None
