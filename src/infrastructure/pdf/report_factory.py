from src.domain.models import ReportPeriod


class ReportFactory:
    _TEMPLATES: dict[ReportPeriod, str] = {
        ReportPeriod.DAILY: "report_daily.html",
        ReportPeriod.WEEKLY: "report_weekly.html",
    }

    def template_for(self, period: ReportPeriod) -> str:
        return self._TEMPLATES[period]
