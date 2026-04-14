from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Donation
from .serializers import DonationSerializer, UserDonationSerializer
from projects.models import Project

# ─── calculate progress ─────────────────────────────────────────────────────────
def calculate_progress(project):
    total = sum([d.amount for d in project.donations.all()])
    target = project.total_target
    progress = (total / target) * 100 if target > 0 else 0
    return {
        "total_donations": float(total),
        "target": float(target),
        "progress": progress,
    }


# ─── Donate Endpoint ─────────────────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def donate(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"error": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = DonationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    #save donation
    serializer.save(user=request.user, project=project)

    return Response(
        {
            "message": "Donation successful",
            "data": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# ─── Project Details + Progress ─────────────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def project_details(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"error": "Project not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    progress = calculate_progress(project)

    data = {
        "id": project.id,
        "title": project.title,
        "details": project.details,
        "target": project.total_target,
        "progress": progress,
    }

    return Response(data, status=status.HTTP_200_OK)


# ─── User Donations History ─────────────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_donations(request):
    donations = Donation.objects.filter(user=request.user)
    serializer = UserDonationSerializer(donations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)