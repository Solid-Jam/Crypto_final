import sqlite3
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from models.asset import Asset, AssetBase, AssetCreate
from database import get_db_connection
from auth.security import get_api_key

router = APIRouter()

@router.get("/", response_model=List[Asset])
def get_assets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, symbol, type, price FROM assets")
    assets = cursor.fetchall()
    conn.close()

    return [
        {
            "id": asset[0],
            "name": asset[1],
            "symbol": asset[2],
            "type": asset[3],
            "price": asset[4],
        }
        for asset in assets
    ]


@router.post("/", response_model=Asset)
def create_asset(asset: AssetCreate, _: str = Depends(get_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO assets (name, symbol, type, price) VALUES (?, ?, ?, ?)",
            (asset.name, asset.symbol, asset.type, asset.price)
        )
        conn.commit()
        asset_id = cursor.lastrowid
        return Asset(id=asset_id, **asset.dict())

    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The asset '{asset.name}' already exists."
        )
    finally:
        conn.close()


@router.put("/{asset_id}", response_model=Asset)
def update_asset(asset_id: int, asset: AssetCreate, _: str = Depends(get_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE assets SET name = ?, symbol = ?, type = ?, price = ? WHERE id = ?",
        (asset.name, asset.symbol, asset.type, asset.price, asset_id)
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Asset not found")

    conn.commit()
    conn.close()
    return Asset(id=asset_id, **asset.dict())


@router.delete("/{asset_id}", response_model=dict)
def delete_asset(asset_id: int, _: str = Depends(get_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assets WHERE id = ?", (asset_id,))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Asset not found")

    conn.commit()
    conn.close()
    return {"detail": "Asset deleted"}
