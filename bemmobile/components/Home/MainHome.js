import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Image,
} from 'react-native';
import { Searchbar, Chip } from 'react-native-paper';
import MyStyles , { colors } from '../../styles/MyStyles';
import { useNavigation } from '@react-navigation/native';
import Apis, { endpoints } from '../../configs/Apis';
import AsyncStorage from '@react-native-async-storage/async-storage';

const MainHome = () => {
  // Danh mục cứng
  const [categories] = useState([
    { id: 'music', name: 'Music' },
    { id: 'sports', name: 'Sports' },
    { id: 'seminar', name: 'Seminar' },
    { id: 'conference', name: 'Conference' },
    { id: 'festival', name: 'Festival' },
    { id: 'workshop', name: 'Workshop' },
    { id: 'party', name: 'Party' },
    { id: 'competition', name: 'Competition' },
    { id: 'other', name: 'Other' },
  ]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [q, setQ] = useState('');
  const [cateId, setCateId] = useState(null);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false); // Added refreshing state
  const navigation = useNavigation();


  // Lấy danh sách sự kiện
  const loadEvents = async () => {
    if (page > 0) {
      try {
        setLoading(true);
        setError(null);
        let url = `${endpoints['events']}?page=${page}`;
        if (q) url += `&q=${q}`;
        if (cateId) url += `&category=${cateId}`; // Lưu ý: API cần hỗ trợ lọc theo category

        console.log('Calling API:', `${Apis.defaults.baseURL}${url}`);
        const res = await Apis.get(url);

        console.log('API response status:', res.status);
        // console.log('API response data:', res.data);

        const newEvents = Array.isArray(res.data.results) ? res.data.results : [];
        // console.log('Events data:', newEvents);

        setEvents((prevEvents) =>
          page === 1 ? newEvents : [...prevEvents, ...newEvents]
        );

        if (!res.data.next) {
          setPage(0);
        }
      } catch (error) {
        console.error('Error loading events:', error.message, error.config?.url);
        setError(`Failed to load events: ${error.message} (${error.config?.url || 'Unknown URL'})`);
      } finally {
        setLoading(false);
        setRefreshing(false); // Stop refreshing when load completes
      }
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      loadEvents();
    }, 500);

    return () => clearTimeout(timer);
  }, [q, page, cateId]);

  const loadMore = () => {
    if (!loading && page > 0) {
      setPage(page + 1);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    setPage(1);
    setEvents([]); // Clear old events to reload fresh
  };

  const search = (value, callback) => {
    setPage(1);
    setEvents([]); // Xóa dữ liệu cũ khi tìm kiếm
    callback(value);
  };

  const renderEventItem = ({ item }) => {
    // Xử lý poster URL đầy đủ

    let posterUrl = item.poster;
    if (posterUrl && !posterUrl.startsWith('http')) {
      // Đảm bảo có dấu "/" giữa baseURL và poster path
      posterUrl = `${Apis.defaults.baseURL.replace(/\/+$/, '')}/${posterUrl.replace(/^\/+/, '')}`;
    }

    return (
      <TouchableOpacity
        style={MyStyles.eventItem}
        onPress={() => navigation.navigate('EventDetails', { event: item })}
      >
        <Image
          source={{ uri: posterUrl || 'https://via.placeholder.com/60' }}
          style={MyStyles.eventImage}
        />
        <View style={MyStyles.eventContent}>
          <Text style={MyStyles.eventTitle}>{item.title || 'Untitled'}</Text>
          <Text style={MyStyles.eventDetail}>
            Date: {item.start_time ? new Date(item.start_time).toLocaleDateString() : 'N/A'}
          </Text>
          <Text style={MyStyles.eventDetail}>Location: {item.location || 'N/A'}</Text>
        </View>
      </TouchableOpacity>
    );
  };

  // Đảm bảo events là mảng trước khi truyền vào FlatList
  const safeEvents = Array.isArray(events) ? events : [];

  return (
    <SafeAreaView style={MyStyles.container}>
      <View style={MyStyles.scrollContainer}>
        {/* Hiển thị lỗi nếu có */}
        {error && (
          <View style={{ padding: 10, backgroundColor: colors.blueLight, marginBottom: 10 }}>
            <Text style={{ color: colors.blue }}>{error}</Text>
          </View>
        )}

        {/* Thanh tìm kiếm */}
        <Searchbar
          placeholder="Search events..."
          onChangeText={(text) => search(text, setQ)}
          value={q}
          style={MyStyles.searchbar}
        />

        {/* Danh mục sự kiện */}
        <View style={[MyStyles.row, MyStyles.wrap]}>
          <TouchableOpacity onPress={() => search(null, setCateId)}>
            <Chip
              style={[MyStyles.chip, cateId === null && MyStyles.chipSelected]}
              textStyle={[
                MyStyles.chipText,
                cateId === null && MyStyles.chipTextSelected,
              ]}
              icon="label"
            >
              All
            </Chip>
          </TouchableOpacity>
          {categories.map((c) => (
            <TouchableOpacity
              key={`Cate${c.id}`}
              onPress={() => search(c.id, setCateId)}
            >
              <Chip
                style={[MyStyles.chip, cateId === c.id && MyStyles.chipSelected]}
                textStyle={[
                  MyStyles.chipText,
                  cateId === c.id && MyStyles.chipTextSelected,
                ]}
                icon="label"
              >
                {c.name}
              </Chip>
            </TouchableOpacity>
          ))}
        </View>

        {/* Danh sách sự kiện */}
        {loading && page === 1 ? (
          <ActivityIndicator size="large" color={colors.bluePrimary} />
        ) : safeEvents.length === 0 ? (
          <Text style={{ textAlign: 'center', marginTop: 20 }}>No events found</Text>
        ) : (
          <FlatList
            data={safeEvents}
            renderItem={renderEventItem}
            keyExtractor={(item) => item.id.toString()}
            onEndReached={loadMore}
            onEndReachedThreshold={0.5}
        ListFooterComponent={
          loading && page > 1 && <ActivityIndicator size="large" color={colors.bluePrimary} />
        }
        refreshing={refreshing} // Added refreshing prop
        onRefresh={onRefresh} // Added onRefresh prop
      />
    )}
  </View>
</SafeAreaView>
  );
};

export default MainHome;
