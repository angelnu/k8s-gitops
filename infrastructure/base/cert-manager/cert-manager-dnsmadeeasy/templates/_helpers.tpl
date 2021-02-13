{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "example-webhook.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "example-webhook.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "example-webhook.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "example-webhook.labels" -}}
helm.sh/chart: {{ include "example-webhook.chart" . }}
{{ include "example-webhook.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "example-webhook.selectorLabels" -}}
app.kubernetes.io/name: {{ include "example-webhook.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "example-webhook.selfSignedIssuer" -}}
{{ printf "%s-selfsign" (include "example-webhook.fullname" .) }}
{{- end -}}

{{- define "example-webhook.rootCAIssuer" -}}
{{ printf "%s-ca" (include "example-webhook.fullname" .) }}
{{- end -}}

{{- define "example-webhook.rootCACertificate" -}}
{{ printf "%s-ca" (include "example-webhook.fullname" .) }}
{{- end -}}

{{- define "example-webhook.servingCertificate" -}}
{{ printf "%s-webhook-tls" (include "example-webhook.fullname" .) }}
{{- end -}}
