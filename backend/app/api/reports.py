from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, Response

from app.core.deps import CurrentUser, DbSession
from app.services.reports import load_order, render_report_html, render_report_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{order_id}/html", response_class=HTMLResponse)
def report_html(order_id: int, db: DbSession, _: CurrentUser) -> str:
    order = load_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return render_report_html(db, order)


@router.get("/{order_id}/pdf")
def report_pdf(order_id: int, db: DbSession, _: CurrentUser) -> Response:
    order = load_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    pdf = render_report_pdf(db, order)
    filename = f"report-{order.order_number}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
