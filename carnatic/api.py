# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

from carnatic import models

from rest_framework import generics
from rest_framework import serializers

class ArtistInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Artist
        fields = ['mbid', 'name']

class ComposerInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Composer
        fields = ['mbid', 'name']

class WorkInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Work
        fields = ['mbid', 'title']

class RecordingInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recording
        fields = ['mbid', 'title']

class RaagaInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Raaga
        fields = ['id', 'name']

class TaalaInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taala
        fields = ['id', 'name']

class ConcertInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Concert
        fields = ['mbid', 'title']

class InstrumentInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = ['id', 'name']


class WithBootlegAPIView(object):
    @property
    def with_bootlegs(self):
        is_staff = self.request.user.is_staff
        with_bootlegs = self.request.QUERY_PARAMS.get('with_bootlegs', None)
        with_bootlegs = with_bootlegs is not None and is_staff
        return with_bootlegs

    @property
    def is_staff(self):
        return self.request.user.is_staff


class TaalaList(generics.ListAPIView):
    queryset = models.Taala.objects.all()
    serializer_class = TaalaInnerSerializer

class TaalaDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(source='artists')
    works = WorkInnerSerializer(source='works')
    composers = ComposerInnerSerializer(source='composers')
    aliases = serializers.RelatedField(many=True, source='aliases.all')

    class Meta:
        model = models.Taala
        fields = ['id', 'name', 'common_name', 'aliases', 'artists', 'works', 'composers']

class TaalaDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Taala.objects.all()
    serializer_class = TaalaDetailSerializer


class RaagaList(generics.ListAPIView):
    queryset = models.Raaga.objects.all()
    serializer_class = RaagaInnerSerializer

class RaagaDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(source='artists')
    works = WorkInnerSerializer(source='works')
    composers = ComposerInnerSerializer(source='composers')
    aliases = serializers.RelatedField(many=True, source='aliases.all')

    class Meta:
        model = models.Raaga
        fields = ['id', 'name', 'common_name', 'aliases', 'artists', 'works', 'composers']

class RaagaDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Raaga.objects.all()
    serializer_class = RaagaDetailSerializer


class InstrumentList(generics.ListAPIView):
    queryset = models.Instrument.objects.all()
    serializer_class = InstrumentInnerSerializer

class InstrumentDetailSerializer(serializers.ModelSerializer):
    artists = ArtistInnerSerializer(source='artists')

    class Meta:
        model = models.Instrument
        fields = ['id', 'name', 'artists']

class InstrumentDetail(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = models.Instrument.objects.all()
    serializer_class = InstrumentDetailSerializer


class WorkList(generics.ListAPIView):
    queryset = models.Work.objects.all()
    serializer_class = WorkInnerSerializer

class WorkDetailSerializer(serializers.ModelSerializer):
    composers = ComposerInnerSerializer(source='composers', many=True)
    raagas = RaagaInnerSerializer(source='raaga', many=True)
    taalas = TaalaInnerSerializer(source='taala', many=True)
    recordings = serializers.SerializerMethodField('recording_list')

    class Meta:
        model = models.Work
        fields = ['mbid', 'title', 'composers', 'raagas', 'taalas', 'recordings']

    def recording_list(self, ob):
        recordings = ob.recording_set.with_bootlegs(self.with_bootlegs)
        return RecordingInnerSerializer(recordings, many=True).data

class BootlegWorkDetailSerializer(WorkDetailSerializer):
    with_bootlegs = True

class NoBootlegWorkDetailSerializer(WorkDetailSerializer):
    with_bootlegs = False

class WorkDetail(generics.RetrieveAPIView, WithBootlegAPIView):
    lookup_field = 'mbid'
    queryset = models.Work.objects.all()

    def get_serializer_class(self):
        if self.with_bootlegs:
            return BootlegWorkDetailSerializer
        else:
            return NoBootlegWorkDetailSerializer


class RecordingList(generics.ListAPIView, WithBootlegAPIView):
    serializer_class = RecordingInnerSerializer

    def get_queryset(self):
        return models.Recording.objects.with_bootlegs(self.with_bootlegs)


class RecordingDetailSerializer(serializers.ModelSerializer):
    concert = ConcertInnerSerializer(source='concert_set.get')
    artists = ArtistInnerSerializer(source='all_artists')
    raaga = RaagaInnerSerializer(source='raaga')
    taala = TaalaInnerSerializer(source='taala')
    work = RecordingInnerSerializer(source='work')

    class Meta:
        model = models.Recording
        fields = ['mbid', 'title', 'artists', 'raaga', 'taala', 'work', 'concert']

class RecordingDetail(generics.RetrieveAPIView, WithBootlegAPIView):
    lookup_field = 'mbid'
    queryset = models.Recording.objects.all()
    serializer_class = RecordingDetailSerializer

    def get_queryset(self):
        # We only check if the user is staff here - you do not
        # need to add ?with_bootlegs if you specify the mbid
        # of a bootleg recording
        return models.Recording.objects.with_bootlegs(self.is_staff)


class ArtistList(generics.ListAPIView):
    queryset = models.Artist.objects.all()
    serializer_class = ArtistInnerSerializer

class ArtistDetailSerializer(serializers.ModelSerializer):
    concerts = serializers.SerializerMethodField('concert_list')
    instruments = InstrumentInnerSerializer(source='instruments')
    recordings = serializers.SerializerMethodField('recording_list')

    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'concerts', 'instruments', 'recordings']

    def concert_list(self, ob):
        concerts = ob.concerts(with_bootlegs=self.with_bootlegs)
        cs = ConcertInnerSerializer(concerts, many=True)
        return cs.data

    def recording_list(self, ob):
        recordings = ob.recordings(with_bootlegs=self.with_bootlegs)
        rs = RecordingInnerSerializer(recordings, many=True)
        return rs.data

class BootlegArtistDetailSerializer(ArtistDetailSerializer):
    with_bootlegs = True

class NoBootlegArtistDetailSerializer(ArtistDetailSerializer):
    with_bootlegs = False

class ArtistDetail(generics.RetrieveAPIView, WithBootlegAPIView):
    lookup_field = 'mbid'
    queryset = models.Artist.objects.all()

    def get_serializer_class(self):
        if self.with_bootlegs:
            return BootlegArtistDetailSerializer
        else:
            return NoBootlegArtistDetailSerializer


class ConcertList(generics.ListAPIView, WithBootlegAPIView):
    queryset = models.Concert.objects.all()
    serializer_class = ConcertInnerSerializer

    def get_queryset(self):
        return models.Concert.objects.with_bootlegs(self.with_bootlegs)

class ConcertArtistSerializer(serializers.ModelSerializer):
    name = serializers.Field(source='performer.name')
    mbid = serializers.Field(source='performer.mbid')
    instrument = serializers.Field(source='instrument.name')

    class Meta:
        model = models.Artist
        fields = ['mbid', 'name', 'instrument']

class ConcertDetailSerializer(serializers.ModelSerializer):
    recordings = RecordingInnerSerializer(source='tracklist', many=True)
    artists = ConcertArtistSerializer(source='performers')
    concert_artists = ArtistInnerSerializer(source='artists')

    class Meta:
        model = models.Concert
        fields = ['mbid', 'title', 'recordings', 'artists', 'concert_artists']

class ConcertDetail(generics.RetrieveAPIView, WithBootlegAPIView):
    lookup_field = 'mbid'
    serializer_class = ConcertDetailSerializer

    def get_queryset(self):
        # We only check if the user is staff here - you do not
        # need to add ?with_bootlegs if you specify the mbid
        # of a bootleg concert
        return models.Concert.objects.with_bootlegs(self.is_staff)
