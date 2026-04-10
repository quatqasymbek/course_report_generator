from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def plot_course_overview(tests_df: pd.DataFrame, course_id: str):
    df = tests_df[tests_df["course_id"].astype(str) == str(course_id)].copy()
    if df.empty:
        return None

    values = [
        df["pre_test_score"].mean(),
        df["post_test_score"].mean(),
        df["knowledge_gain"].mean(),
    ]
    labels = ["Входное", "Итоговое", "Прирост"]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, values)
    ax.set_title("Итоги тестирования по курсу")
    ax.set_ylabel("Среднее значение")
    return fig


def plot_region_gains(region_summary: pd.DataFrame, course_id: str):
    df = region_summary[region_summary["course_id"].astype(str) == str(course_id)].copy()
    if df.empty:
        return None

    df = df.sort_values("gain_mean", ascending=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df["region_canonical"], df["gain_mean"])
    ax.set_title("Прирост знаний по регионам")
    ax.set_ylabel("Прирост")
    ax.tick_params(axis="x", rotation=45)
    return fig


def plot_course_score_distribution(tests_df: pd.DataFrame, course_id: str):
    df = tests_df[tests_df["course_id"].astype(str) == str(course_id)].copy()
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(df["pre_test_score"].dropna(), bins=10, alpha=0.6, label="Входное")
    ax.hist(df["post_test_score"].dropna(), bins=10, alpha=0.6, label="Итоговое")
    ax.set_title("Распределение баллов")
    ax.set_xlabel("Балл")
    ax.set_ylabel("Количество слушателей")
    ax.legend()
    return fig


def plot_csat_content_by_region(surveys_df: pd.DataFrame, course_id: str):
    df = surveys_df[surveys_df["course_id"].astype(str) == str(course_id)].copy()
    if df.empty or "region_canonical" not in df.columns:
        return None

    summary = (
        df.groupby("region_canonical", dropna=False)["content_score"]
        .agg(lambda s: round(((s == 10).sum() / s.notna().sum()) * 100, 2) if s.notna().sum() else 0)
        .reset_index(name="excellent_pct")
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(summary["region_canonical"], summary["excellent_pct"])
    ax.set_title("Удовлетворенность содержанием по регионам")
    ax.set_ylabel("% оценок «отлично»")
    ax.tick_params(axis="x", rotation=45)
    return fig


def plot_csat_organization_by_region(surveys_df: pd.DataFrame, course_id: str):
    df = surveys_df[surveys_df["course_id"].astype(str) == str(course_id)].copy()
    if df.empty or "region_canonical" not in df.columns:
        return None

    summary = (
        df.groupby("region_canonical", dropna=False)["trainer_organization_score"]
        .agg(lambda s: round(((s == 5).sum() / s.notna().sum()) * 100, 2) if s.notna().sum() else 0)
        .reset_index(name="excellent_pct")
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(summary["region_canonical"], summary["excellent_pct"])
    ax.set_title("Удовлетворенность организацией по регионам")
    ax.set_ylabel("% оценок «отлично»")
    ax.tick_params(axis="x", rotation=45)
    return fig


def plot_csat_instructors_by_region(surveys_df: pd.DataFrame, course_id: str):
    df = surveys_df[surveys_df["course_id"].astype(str) == str(course_id)].copy()
    if df.empty or "region_canonical" not in df.columns:
        return None

    summary = (
        df.groupby("region_canonical", dropna=False)["trainer_mastery_score"]
        .agg(lambda s: round(((s == 5).sum() / s.notna().sum()) * 100, 2) if s.notna().sum() else 0)
        .reset_index(name="excellent_pct")
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(summary["region_canonical"], summary["excellent_pct"])
    ax.set_title("Оценка работы тренеров по регионам")
    ax.set_ylabel("% оценок «отлично»")
    ax.tick_params(axis="x", rotation=45)
    return fig
